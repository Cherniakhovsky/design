from aiohttp import web

from api.settings import Settings
from api.views import ImagesView

import aiohttp_cors
import api.mongo as mongo


# def setup_routes(app):
#     app.router.add_view('/images/', ImagesView)

# def on_prepare(request, response):
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Content-Type'] = 'application/json'

def make_app():
    app = web.Application()
    # cors = aiohttp_cors.setup(app)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    # resource = cors.add(app.router.add_resource("/images/"))
    # route = cors.add(
    #     resource.add_route("GET", handler), {
    #         "http://client.example.org": aiohttp_cors.ResourceOptions(
    #             allow_credentials=True,
    #             expose_headers=("X-Custom-Server-Header",),
    #             allow_headers=("X-Requested-With", "Content-Type"),
    #             max_age=3600,
    #         )
    #     })

    # app.router.add_view('/images/', ImagesView)
    
    # import pydevd
    # pydevd.settrace('192.168.1.229', port=5555, stdoutToServer=True, stderrToServer=True)
    #
    # app.on_response_prepare(on_prepare)

    app['settings'] = Settings()

    # cors.add(app.router.add_view("/images/", ImagesView), webview=True)
    # cors.add(app.router.add_route("*", "/resource", CorsView), webview=True)

    # setup_routes(app)

    # app.router.add_view('/images/', ImagesView)
    
    # import pydevd
    # pydevd.settrace('192.168.1.229', port=5555, stdoutToServer=True, stderrToServer=True)
    cors.add(app.router.add_route("*", "/api/images/", ImagesView), webview=True)
    
    # for route in list(app.router.routes()):
    #     cors.add(route)

    mongo.setup(app)
    return app


def main():
    app = make_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
