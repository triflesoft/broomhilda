#!/usr/bin/env python3

from broomhilda.facade.server.server11 import Server11
from broomhilda.extras.handlers.template import Jinja2HandlerBase
from broomhilda.extras.handlers.template import jinja2_template
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.extras.routes import Router
from datetime import datetime
from jinja2 import Environment
from jinja2 import FileSystemLoader
from os.path import dirname


class DefaultHandler(Jinja2HandlerBase):
    def __init__(self):
        # Jinja2HandlerBase.__init__ will perform all kinds of black magic.
        super().__init__(Environment(
            loader=FileSystemLoader(dirname(__file__)),
            # Always enable async.
            enable_async=True))

    @jinja2_template('test_jinja2_handler.html')
    async def get(self, request, response):
        # Note that handler returns data
        return { 'size': 123456789, 'time': datetime.now()}

router = Router()
router.add('/', DefaultHandler())

# HTTP 1.1 server
server = Server11(
    middlewares=[RoutingMiddleware(router)],
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Execute the following commands to test:')
print('curl -i http://localhost:8080/')

from webbrowser import open

open('http://localhost:8080/')

server.run(port=8080)
