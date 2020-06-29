import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_uri = 'mongodb://mongo'
    mongo_db_name = 'design'
    mongo_host = '127.0.0.1'
    mongo_port = 27017

    minio_uri = '127.0.0.1:9000'
    minio_access_key = os.environ.get('MINIO_ACCESS_KEY')
    minio_secret_key = os.environ.get('MINIO_SECRET_KEY')

