from aiohttp import web

from api.models import Image
from api.minio import MinioHandler

from aiohttp_cors import CorsViewMixin

IMAGE_WIDTH = 800

minioClient = MinioHandler()


class ImagesView(web.View, CorsViewMixin):

    async def get(self):
        images = await Image.get_images(self.request.app['mongo'])

        result = [{'imageUrl': minioClient.get_url(im_data, IMAGE_WIDTH)}
                  for im_data in images]

        return web.json_response(result)
