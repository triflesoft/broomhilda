from broomhilda.facade.server.base11 import Server11Base
from broomhilda.facade.server.requests import ServerRequest
from broomhilda.facade.server.responses import ServerResponse


class Connection11Curio(object):
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

        await self.socket.sendall(data)


class Server11Curio(Server11Base):
    def __init__(self,
        middlewares=[],
        default_headers=[],
        prepare_workers=[],
        process_workers=[],
        cleanup_workers=[]):
        super().__init__(middlewares, default_headers, prepare_workers, process_workers, cleanup_workers)

    async def _client_connected(self, client_socket, client_address):
        from socket import SHUT_RDWR

        connection = Connection11Curio(self, client_socket, client_address)

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

        await client_socket.shutdown(SHUT_RDWR)
        await client_socket.close()

    async def _server_listener(self, host, port):
        from curio import TaskGroup
        from curio.socket import AF_INET
        from curio.socket import SOCK_STREAM
        from curio.socket import SOL_SOCKET
        from curio.socket import SO_REUSEADDR
        from curio.socket import SO_REUSEPORT
        from curio.socket import socket
        from sys import platform

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

        if platform == 'linux':
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, True)

        server_socket.bind((host, port))
        server_socket.listen(1024)

        async with TaskGroup() as client_group:
            async with server_socket:
                while True:
                    client_socket, client_address = await server_socket.accept()

                    await client_group.spawn(self._client_connected, client_socket, client_address, ignore_result=True)

    async def _main(self, host, port):
        from curio import TaskGroup

        if len(self._prepare_workers) > 0:
            async with TaskGroup() as task_group:
                for worker in self._prepare_workers:
                    await task_group.spawn(worker)

                await task_group.join()

        async with TaskGroup() as task_group:
            await task_group.spawn(self._server_listener, host, port)

            for worker in self._process_workers:
                await task_group.spawn(worker)

            await task_group.join()

        if len(self._cleanup_workers) > 0:
            async with TaskGroup() as task_group:
                for worker in self._cleanup_workers:
                    await task_group.spawn(worker)

                await task_group.join()

    def run(self, host='0.0.0.0', port=80):
        from curio import run as _run

        _run(self._main, host, port)
