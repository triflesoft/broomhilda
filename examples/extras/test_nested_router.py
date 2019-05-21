#!/usr/bin/env python3

from broomhilda.facade.server.server11 import Server11
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.extras.routes import Router


async def inner1(request, response, a, b):
    await response.send_text(f'INNER #1 {a} {b}')

async def inner2(request, response, a, b):
    await response.send_text(f'INNER #2 {a} {b}')

async def outer(request, response, a, b):
    await response.send_text(f'OUTER {a} {b}')


router1 = Router()
router1.add('/<b:int>/', inner1, 'GET')

router2 = Router()
router2.add('-<b:int>', inner2, 'GET')

router_top = Router()
# note that one '/' will be collapsed so final path is '/<a:int>/<b:int>/', not '/<a:int>//<b:int>/'
router_top.add('/<a:int>/', router1)
router_top.add('/<a:int>', router1)
router_top.add('/<a:int>/', router2)
router_top.add('/<a:int>', router2)
router_top.add('/<a:int>.<b:int>', outer, 'GET')

# HTTP 1.1 server
server = Server11(
    middlewares=[RoutingMiddleware(router_top)],
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Execute the following commands to test:')
print('curl -i http://localhost:8080/1/4/')
print('curl -i http://localhost:8080/2/-5')
print('curl -i http://localhost:8080/3-6')

from webbrowser import open

open('http://localhost:8080/1/4/')
open('http://localhost:8080/2/-5')
open('http://localhost:8080/3-6')

server.run(port=8080)
