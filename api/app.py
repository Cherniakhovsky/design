import aiohttp_cors

from aiohttp import web

import api.mongo as mongo
from api.settings import Settings
from api.views import ImagesView


def make_app():
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    app['settings'] = Settings()

    cors.add(app.router.add_route("*", "/api/images/", ImagesView), webview=True)

    mongo.setup(app)
    return app


def main():
    app = make_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
