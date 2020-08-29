import copy
import datetime as dt
import filetype
import json
import logging
import os

from minio import Minio
from PIL import Image
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from resizeimage import resizeimage


class MinioHandler:
    _client: Minio = Minio('127.0.0.1:9000',
                     access_key='Q3AM3UQ867SPQQA43P2F',
                     secret_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
                     secure=False)

    def __init__(self):

        self._default_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "*"
                        ]
                    },
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads"
                    ],
                    "Resource": [
                        "arn:aws:s3:::{bucket}"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "*"
                        ]
                    },
                    "Action": [
                        "s3:DeleteObject",
                        "s3:GetObject",
                        "s3:ListMultipartUploadParts",
                        "s3:PutObject",
                        "s3:AbortMultipartUpload"
                    ],
                    "Resource": [
                        "arn:aws:s3:::{bucket}/*"
                    ]
                }
            ]
        }

    def _create_bucket(self, bucket: str) -> None:
        try:
            logging.info(f'Creating a new bucket [{bucket}]')
            self._client.make_bucket(bucket)
            self._set_bucket_policy(bucket)
            return None
        except Exception:
            logging.exception(f'Error occured while creating the bucket [{bucket}]')

    def _set_bucket_policy(self, bucket: str, policy: dict = None) -> None:
        if policy is None:
            policy = copy.deepcopy(self._default_policy)
        resource = policy['Statement'][0]['Resource'][0].format(bucket=bucket)
        policy['Statement'][0]['Resource'][0] = resource
        policy['Statement'][1]['Resource'][0] = f'{resource}/*'

        try:
            self._client.set_bucket_policy(bucket_name=bucket,
                                           policy=json.dumps(policy))
            return None
        except Exception:
            logging.exception(f'Unable to set bucket policy: {policy}')


IMAGE_WIDTH = 800
ALLOWED_EXTENSIONS = ['png', 'jpg']
IMAGES_FOLDER = 'design_test'
IMAGES_FOLDER_PATH = os.path.join('/'.join(os.getcwd().split('/')[:3]),
                                  'Downloads', IMAGES_FOLDER)

minioClient = MinioHandler()

mongoClient = MongoClient(host='127.0.0.1',
                          port=27017,
                          connect=True)

db = mongoClient['design']


def find_images_path():
    images_path = []
    for root, dirs, files in os.walk(IMAGES_FOLDER_PATH, topdown=False):
        for name in files:
            images_path.append(os.path.join(root, name))
    return dirs, images_path


def upload_data_in_minio_and_mongo(images_path):

    mongo_data = []
    for image_path in images_path:

        filetype_obj = filetype.guess(image_path)

        if filetype_obj and filetype_obj.extension in ALLOWED_EXTENSIONS:
            splitted_path = image_path.split(os.sep)
            image_name, _ = os.path.splitext(splitted_path[-1])
            ext = filetype_obj.extension

            bucket = splitted_path[-2]

            if not minioClient._client.bucket_exists(bucket):
                minioClient._create_bucket(bucket)
            try:
                resized_img_name, resized_img_path = resize_image(
                    image_path, image_name, ext, IMAGE_WIDTH)
            except Exception as err:
                print(err)
                continue

            save_img_to_minio(bucket, image_path, image_name, ext)
            save_img_to_minio(bucket, resized_img_path, resized_img_name, ext)

            mongo_data.append({'_id': image_name, 'ext': ext})

    try:
        db.images.insert_many(mongo_data)
    except BulkWriteError as err:
        print('BulkWriteError during inserting to mongo: ', err)
    except Exception as err:
        print('Error during inserting to mongo: ', err)

    print('OK')


def resize_image(image_path, image_name, ext, width_size):
    try:
        with open(image_path, 'rb') as f:
            with Image.open(f) as img:
                resized_img = resizeimage.resize_width(img, width_size)
                resized_img_name = f'{image_name}_width_{width_size}'
                resized_img_path = f'/tmp/{resized_img_name}.{ext}'
                resized_img.save(resized_img_path)
    except Exception as err:
        print(err)
        raise Exception

    return resized_img_name, resized_img_path


def save_img_to_minio(bucket, resized_img_path, resized_img_name, ext):
    try:
        with open(resized_img_path, 'rb') as f:
            file_stat = os.stat(resized_img_path)
            minioClient._client.put_object(bucket, f'{resized_img_name}.{ext}',
                                 f, file_stat.st_size)
    except Exception as err:
        print(err)


def drop_minio_and_mongo_data():
    buckets = minioClient._client.list_buckets()

    for bucket in buckets:
        objects = minioClient._client.list_objects(bucket.name)
        for object in objects:
            try:
                minioClient._client.remove_object(object.bucket_name, object.object_name)
            except Exception as err:
                print(err)

    for bucket in buckets:
        try:
            minioClient._client.remove_bucket(bucket.name)
        except Exception as err:
            print(err)

    db.images.drop()


if __name__ == '__main__':
    drop_minio_and_mongo_data()
    buckets, images_path = find_images_path()
    upload_data_in_minio_and_mongo(images_path)
