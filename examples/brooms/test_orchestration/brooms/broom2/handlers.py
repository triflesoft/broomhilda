class HandlerC:
    async def get(self, request, response):
        await response.send_text(f'HandlerC #1.')

class HandlerD:
    async def get(self, request, response, id):
        await response.send_text(f'HandlerD #1. ID = {id}')