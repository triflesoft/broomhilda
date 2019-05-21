#!/usr/bin/env python3

from broomhilda.extras.routes import Router
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.facade.server.server11 import Server11


# Class method names shoud match HTTP method names.
# Supported method names are 'connect', 'delete', 'get', 'head', 'options', 'patch', 'post', 'put', 'trace'.

class NoParameter(object):
    async def get(self, request, response):
        await response.send_text('No parameters')


class ForceError(object):
    async def get(self, request, response):
        raise Exception()


class IntParameter(object):
    async def get(self, request, response, parameter):
        await response.send_text(f'Value of int parameter is "{parameter}", type is {type(parameter)}.')


class StrParameter(object):
    async def get(self, request, response, parameter):
        await response.send_text(f'Value of str parameter is "{parameter}", type is {type(parameter)}.')


class SlugParameter(object):
    async def get(self, request, response, parameter):
        await response.send_text(f'Value of slug parameter is "{parameter}", type is {type(parameter)}.')


class UuidParameter(object):
    async def get(self, request, response, parameter):
        await response.send_text(f'Value of uuid parameter is "{parameter}", type is {type(parameter)}.')


class PathParameter(object):
    async def get(self, request, response, parameter):
        await response.send_text(f'Value of path parameter is "{parameter}", type is {type(parameter)}.')


# Note that handler instances, not classes are passer to the router.
router = Router()
router.add('/none/', NoParameter())
router.add('/error/', ForceError())
router.add('/int/<parameter:int>/', IntParameter())
# Could use router.add('/str/<parameter>', StrParameter()) since parameters are str by default
router.add('/str/<parameter:str>/', StrParameter())
router.add('/slug/<parameter:slug>/', SlugParameter())
# You can explicitly specify method names.
# You can specify method name in any case.
# You can specify one method name as a string or many method names as any iterable.
# Specifying method name without corresponding class method is not an error.
router.add('/uuid/<parameter:uuid>/', UuidParameter(), 'GeT')
router.add('/path/<parameter:path>/', PathParameter(), ('GET', 'post'))

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
