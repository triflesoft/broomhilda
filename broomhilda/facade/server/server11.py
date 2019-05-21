from broomhilda.facade.server._curio import Server11Curio
from broomhilda.facade.server._trio import Server11Trio
from broomhilda.facade.server.requests import ServerRequest
from broomhilda.facade.server.responses import ServerResponse
from os import environ
from re import split


class Server11(object):
    def __init__(self,
        middlewares=[],
        default_headers=[],
        prepare_workers=[],
        process_workers=[],
        cleanup_workers=[]):
        self._server = None
        backend_names = environ.get('BROOMHILDA_BACKENDS', 'trio')
        backend_names = split(',|;|:| ', backend_names.lower())

        for backend_name in backend_names:
            if backend_name == 'trio':
                self._server = Server11Trio(middlewares, default_headers, prepare_workers, process_workers, cleanup_workers)
            elif backend_name == 'curio':
                self._server = Server11Curio(middlewares, default_headers, prepare_workers, process_workers, cleanup_workers)

        if self._server is None:
            self._server = Server11Trio(middlewares, default_headers, prepare_workers, process_workers, cleanup_workers)

    def run(self, host='0.0.0.0', port=80):
        self._server.run(host, port)
