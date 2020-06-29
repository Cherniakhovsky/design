from pydantic import BaseModel


class Image(BaseModel):

    @staticmethod
    async def get_images(db):
        cursor = db.images.find()
        images = await cursor.to_list(None)

        return images
