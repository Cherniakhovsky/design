from aiohttp import web

from api.models import Image
from api.minio import MinioHandler


minioClient = MinioHandler()


class ImagesView(web.View):

    async def get(self):
        images = await Image.get_images(self.request.app['mongo'])

        image_width = 800

        result = list()
        for image_data in images:
            result.append({'imageUrl': minioClient.get_url(image_data, image_width)})

        return web.json_response(result)
