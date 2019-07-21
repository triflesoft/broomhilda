class Connection11:
    def __init__(self, server, socket, address):
        self.server = server
        self.socket = socket
        self.fileno = self.socket._socket.fileno()
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


class Server11:
    def __init__(self, middlewares=[], default_headers=[], prepare_workers=[], process_workers=[], cleanup_workers=[]):
        self._middlewares = []

        if middlewares:
            self._middlewares += list(middlewares)

        self._default_headers = []

        if default_headers:
            self._default_headers += list(default_headers)

        self._prepare_workers = []

        if prepare_workers:
            self._prepare_workers += list(prepare_workers)

        self._process_workers = []

        if process_workers:
            self._process_workers += list(process_workers)

        self._cleanup_workers = []

        if cleanup_workers:
            self._cleanup_workers += list(cleanup_workers)

    async def _client_connected(self, tcp_server_socket, client_address):
        from broomhilda.facade.server.requests import ServerRequest
        from broomhilda.facade.server.responses import ServerResponse

        try:
            try:
                connection = Connection11(self, tcp_server_socket, client_address)

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
            finally:
                try:
                    await tcp_server_socket.shutdown()
                except:
                    pass

                await tcp_server_socket.close()
        except:
            pass # TODO log errors

    async def _server_listener(self, host, port):
        from broomio import Nursery
        from broomio import TcpListenSocket

        tcp_listen_socket = TcpListenSocket()
        tcp_listen_socket.reuse_addr = True
        tcp_listen_socket.reuse_port = True
        tcp_listen_socket.bind((host, port))
        await tcp_listen_socket.listen(1024)

        async with Nursery() as nursery:
            while True:
                await tcp_listen_socket.accept(nursery, self._client_connected)

    def run(self, host='0.0.0.0', port=80):
        from broomio import Loop

        loop = Loop()
        loop.start_soon(self._server_listener(host, port))
        loop.run()
