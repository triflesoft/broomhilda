#!/usr/bin/env python3

from broomhilda.facade.server.server11 import Server11
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.extras.routes import Router


async def default_handler(request, response):
    await response.send_text('Handler executed.')


# You can provide handling in before()
# If you return True from before() the rest of middlewares as well as matched routing handler called by routing middleware will not be executed.
# Always return True if you send body.
# You cannot change anything in after(), it's too late.
class Middleware(object):
    async def before(self, request, response):
        if request.method == 'POST':
            response.status_code = 200
            await response.send_text('Middleware intercepted request! Handler will not be executed!')
            return True

    async def after(self, request, response):
        pass

router = Router()
router.add('/', default_handler, ('GET', 'POST'))

# HTTP 1.1 server
# Note that middleware instances, not classes are passer to the server.
# RoutingMiddleware should be the last in middleware list.
server = Server11(
    middlewares=(Middleware(), RoutingMiddleware(router)),
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Execute the following commands to test:')
print('curl -i -X GET http://localhost:8080/')
print('curl -i -X POST http://localhost:8080/')

server.run(port=8080)
