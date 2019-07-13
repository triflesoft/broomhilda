#!/usr/bin/env python3

from broomhilda.facade.server.server11 import Server11


# You can provide handling in before()
# If you return True from before() the rest of middlewares will not be executed.
# Always return True if you send body.
# You cannot change anything in after(), it's too late.
class PostMiddleware:
    async def before(self, request, response):
        if request.method == 'POST':
            response.status_code = 200
            await response.send_text('PostMiddleware handled request!')
            return True

    async def after(self, request, response):
        pass

class GetMiddleware:
    async def before(self, request, response):
        if request.method == 'GET':
            response.status_code = 200
            await response.send_text('GetMiddleware handled request!')
            return True

    async def after(self, request, response):
        pass

# HTTP 1.1 server
# Note that middleware instances, not classes are passer to the server.
server = Server11(
    middlewares=(GetMiddleware(), PostMiddleware()),
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Execute the following commands to test:')
print('curl -i -X GET http://localhost:8080/')
print('curl -i -X POST http://localhost:8080/')

server.run(port=8080)
