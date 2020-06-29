from aiohttp import web

from api.settings import Settings
from api.views import ImagesView
import api.mongo as mongo


def setup_routes(app):
    app.router.add_view('/images', ImagesView)


def make_app():
    app = web.Application()
    app['settings'] = Settings()
    setup_routes(app)
    mongo.setup(app)
    return app


def main():
    app = make_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
