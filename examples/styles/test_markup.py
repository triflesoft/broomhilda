#!/usr/bin/env python3

from os.path import dirname
from os.path import join

from broomhilda import BASE_PATH
from broomhilda.extras.handlers.static import StaticHandler
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.extras.routes import Router
from broomhilda.facade.server.server11 import Server11


router = Router()
router.add('/static/theme/<path:path>', StaticHandler(join(BASE_PATH, './styles/themes/default')))
router.add('/<path:path>', StaticHandler(dirname(__file__)))

# HTTP 1.1 server
server = Server11(
    middlewares=[RoutingMiddleware(router)],
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Execute the following commands to test:')
print('curl -i http://localhost:8080/test_markup.html')

from webbrowser import open

open('http://localhost:8080/test_markup.html')

server.run(port=8080)
