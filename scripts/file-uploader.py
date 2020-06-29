import os
import filetype
import datetime as dt

from PIL import Image
from resizeimage import resizeimage

from api.minio import MinioHandler
from api.settings import Settings

from policy import policy_read_only
from pymongo import MongoClient
from pymongo.errors import BulkWriteError


s = Settings()

IMAGE_WIDTH = 800
ALLOWED_EXTENSIONS = ['png', 'jpg']
IMAGES_FOLDER = 'design_test'
IMAGES_FOLDER_PATH = os.path.join('/'.join(os.getcwd().split('/')[:3]),
                                  'Downloads', IMAGES_FOLDER)

minioClient = MinioHandler()

mongoClient = MongoClient(host=s.mongo_host,
                          port=s.mongo_port,
                          connect=True)

db = mongoClient[s.mongo_db_name]


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
    # drop_minio_and_mongo_data()
    # buckets, images_path = find_images_path()
    # upload_data_in_minio_and_mongo(images_path)
    minioClient.get_url('furniture_1')


#http://localhost:9000/furniture/furniture_2_width_800.jpg
