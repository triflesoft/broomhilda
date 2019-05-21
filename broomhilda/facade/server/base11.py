class Server11Base(object):
    def __init__(self, middlewares, default_headers, prepare_workers, process_workers, cleanup_workers):
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
