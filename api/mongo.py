from motor import motor_asyncio


async def create_mongo(app):
    s = app['settings']
    db = motor_asyncio.AsyncIOMotorClient(s.mongo_uri)[s.mongo_db_name]
    app['mongo'] = db


async def close_mongo(app):
    pass


def setup(app):
    app.on_startup.append(create_mongo)
    app.on_cleanup.append(close_mongo)
