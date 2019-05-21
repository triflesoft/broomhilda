"""
from asyncio import get_event_loop
from asyncio import BufferedProtocol
from asyncio import Queue


class TestProtocol(BufferedProtocol):
    def __init__(self):
        self.transport = None
        self.queue = Queue()
        self.buffer_data = bytearray(5)
        self.buffer_used = 0

    async def worker(self):
        data = b''

        while True:
            data += await self.queue.get()
            print(data)
            self.queue.task_done()

            if data.endswith(b'\r\n\r\n'):
                self.transport.write(b'''HTTP/1.1 200 OK
Content-Type: text/html; charset=ISO-8859-1
Content-Length: 5

Hello!!!
''')

    def connection_made(self, transport):
        self.transport = transport
        get_event_loop().create_task(self.worker())

    def connection_lost(self, exc):
        print('connection_lost')

    def pause_writing(self):
        print('pause_writing')

    def resume_writing(self):
        print('resume_writing')

    def get_buffer(self, sizehint):
        result =  memoryview(self.buffer_data)[self.buffer_used:]
        return result

    def buffer_updated(self, nbytes):
        self.buffer_used += nbytes

        if self.buffer_used > 0:
            if self.buffer_used == len(self.buffer_data):
                self.queue.put_nowait(self.buffer_data)
            else:
                self.queue.put_nowait(self.buffer_data[0:self.buffer_used])

            self.buffer_data = bytearray(5)
            self.buffer_used = 0

    def eof_received(self):
        print('eof_received')


async def main():
    server = await loop.create_server(TestProtocol, host='0.0.0.0', port=8080, reuse_address=True, reuse_port=True)
    await server.serve_forever()


loop = get_event_loop()
loop.run_until_complete(main())
"""