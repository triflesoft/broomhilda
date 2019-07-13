class HandlerA:
    async def get(self, request, response):
        await response.send_text(f'HandlerA #1.')

class HandlerB:
    async def get(self, request, response, id):
        await response.send_text(f'HandlerB #1. ID = {id}')
