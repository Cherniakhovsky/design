import json
import logging
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
from api.settings import Settings
import copy


s = Settings()

class MinioHandler:
    _client: Minio = Minio(s.minio_uri,
                           access_key=s.minio_access_key,
                           secret_key=s.minio_secret_key,
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

    def get_url(self, image, image_width):
        image_name = image['_id']
        ext = image['extension']
        bucket, _ = image['_id'].split('_')
        image_name_resized = '_'.join([image_name, f'width_{image_width}'])
        return '/'.join([self._client._endpoint_url, bucket, f'{image_name_resized}.{ext}'])
