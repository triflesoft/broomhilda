#!/usr/bin/env python3

from broomhilda.extras.routes import Router
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.facade.server.server11 import Server11


async def no_parameter(request, response):
    await response.send_text('No parameters')


async def force_error(request, response):
    raise Exception()


async def int_parameter(request, response, parameter):
    await response.send_text(f'Value of int parameter is "{parameter}", type is {type(parameter)}.')


async def str_parameter(request, response, parameter):
    await response.send_text(f'Value of str parameter is "{parameter}", type is {type(parameter)}.')


async def slug_parameter(request, response, parameter):
    await response.send_text(f'Value of slug parameter is "{parameter}", type is {type(parameter)}.')


async def uuid_parameter(request, response, parameter):
    await response.send_text(f'Value of uuid parameter is "{parameter}", type is {type(parameter)}.')


async def path_parameter(request, response, parameter):
    await response.send_text(f'Value of path parameter is "{parameter}", type is {type(parameter)}.')


router = Router()
router.add('/none/', no_parameter, 'GET')
router.add('/error/', force_error, 'GET')
router.add('/int/<parameter:int>/', int_parameter, 'GET')
# Could use router.add('/str/<parameter>', str_parameter, 'GET') since parameters are str by default
router.add('/str/<parameter:str>/', str_parameter, 'GET')
router.add('/slug/<parameter:slug>/', slug_parameter, 'GET')
router.add('/uuid/<parameter:uuid>/', uuid_parameter, 'GET')
router.add('/path/<parameter:path>/', path_parameter, 'GET')

# HTTP 1.1 server
server = Server11(
    middlewares=[RoutingMiddleware(router)],
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Execute the following commands to test:')
print('curl -i http://localhost:8080/none/')
print('curl -i http://localhost:8080/error/')
print('curl -i http://localhost:8080/int/123/')
print('curl -i http://localhost:8080/int/ABC/')
print('curl -i http://localhost:8080/str/123/')
print('curl -i http://localhost:8080/str/ABC/')
print('curl -i http://localhost:8080/str/A~B.C/')
print('curl -i http://localhost:8080/str/ABC/DEF/')
print('curl -i http://localhost:8080/slug/123/')
print('curl -i http://localhost:8080/slug/ABC/')
print('curl -i http://localhost:8080/slug/A~B.C/')
print('curl -i http://localhost:8080/slug/ABC/DEF/')
print('curl -i http://localhost:8080/uuid/51dcdc5d-4e7e-4163-8881-9be86992f3c0/')
print('curl -i http://localhost:8080/uuid/51dcdc5d4e7e416388819be86992f3c0/')
print('curl -i http://localhost:8080/uuid/51dc-dc5d-4e7e-4163-8881-9be8-6992-f3c0/')
print('curl -i http://localhost:8080/path/123/')
print('curl -i http://localhost:8080/path/ABC/')
print('curl -i http://localhost:8080/path/A~B.C/')
print('curl -i http://localhost:8080/path/ABC/DEF/')

server.run(port=8080)
