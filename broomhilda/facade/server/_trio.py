from broomhilda.facade.server.base11 import Server11Base
from broomhilda.facade.server.requests import ServerRequest
from broomhilda.facade.server.responses import ServerResponse


class Connection11Trio(object):
    def __init__(self, server, socket, address):
        self.server = server
        self.socket = socket
        self.address = address
        self.request = None
        self.match_result = None
        self.match_handler = None
        self.match_parameters = None

    async def read_request(self, max_length=65536):
        if max_length <= 0:
            return b''

        return await self.socket.recv(max_length)

    async def write_response(self, data):
        if len(data) == 0:
            return

        with memoryview(data) as buffer:
            total_sent = 0

            while total_sent < len(buffer):
                total_sent += await self.socket.send(buffer[total_sent:])


class Server11Trio(Server11Base):
    def __init__(self,
        middlewares=[],
        default_headers=[],
        prepare_workers=[],
        process_workers=[],
        cleanup_workers=[]):
        super().__init__(middlewares, default_headers, prepare_workers, process_workers, cleanup_workers)

    async def _client_connected(self, client_socket, client_address):
        from socket import SHUT_RDWR

        connection = Connection11Trio(self, client_socket, client_address)

        while True:
            request = ServerRequest(connection)

            if not await request._try_read_headers():
                break

            response = ServerResponse(connection, request.version, status_code=500, headers=self._default_headers)

            for middleware in self._middlewares:
                if await middleware.before(request, response) is True:
                    break

            for middleware in self._middlewares:
                await middleware.after(request, response)

            await response._send_headers()
            await response._send_body(b'')

            if not request.keep_alive:
                break

        client_socket.shutdown(SHUT_RDWR)
        client_socket.close()

    async def _server_listener(self, host, port, task_status):
        from trio import open_nursery
        from trio.socket import AF_INET
        from trio.socket import SOCK_STREAM
        from trio.socket import SOL_SOCKET
        from trio.socket import SO_REUSEADDR
        from trio.socket import SO_REUSEPORT
        from trio.socket import socket
        from sys import platform

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

        if platform == 'linux':
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, True)

        await server_socket.bind((host, port))
        server_socket.listen(1024)

        # We want process_workers to start after server listens to socket
        task_status.started()

        async with open_nursery() as nursery:
            while True:
                client_socket, client_address = await server_socket.accept()

                nursery.start_soon(self._client_connected, client_socket, client_address)

    async def _main(self, host, port):
        from trio import open_nursery

        if len(self._prepare_workers) > 0:
            async with open_nursery() as nursery:
                for worker in self._prepare_workers:
                    nursery.start_soon(worker)

        async with open_nursery() as nursery:
            # We want process_workers to start after server listens to socket
            await nursery.start(self._server_listener, host, port)

            for worker in self._process_workers:
                nursery.start_soon(worker)

        if len(self._cleanup_workers) > 0:
            async with open_nursery() as nursery:
                for worker in self._cleanup_workers:
                    nursery.start_soon(worker)

    def run(self, host='0.0.0.0', port=80):
        from trio import run as _run
        from trio import serve_tcp
        from trio.testing import open_stream_to_socket_listener
        from trio import open_tcp_listeners

        _run(self._main, host, port)
