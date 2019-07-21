__all__ = ['Orchestration']


class Broom: # pylint: disable=R0903
    __slots__ = 'name', 'module', 'middleware_classes', 'prefix', 'handler_classes', 'statics', 'worker_classes'

    def _import_identifier(self, name):
        from importlib import import_module

        if '.' in name:
            module_name, function_name = name.rsplit('.', 1)
            module = import_module(module_name, package=self.module.__name__)

            return getattr(module, function_name)

        return getattr(self.module, name)

    def __init__(self, root_package, name, configuration):
        from collections import defaultdict
        from importlib import import_module

        self.name = name
        self.module = import_module(self.name, package=root_package)
        self.middleware_classes = []

        for middleware_class in configuration.get('middlewares', []):
            self.middleware_classes.append(self._import_identifier(middleware_class))

        routes_configuration = configuration.get('routes', {})

        self.prefix = routes_configuration.get('prefix', '')
        self.handler_classes = defaultdict(list)

        for handler_path, handler_class in routes_configuration.get('handlers', {}).items():
            self.handler_classes[self._import_identifier(handler_class)].append(handler_path)

        self.statics = routes_configuration.get('statics', {})

        self.worker_classes = []

        for worker_class_name in configuration.get('workers', []):
            self.worker_classes.append(self._import_identifier(worker_class_name))


class _TarjanStronglyConnectedComponentsNode: # pylint: disable=R0903
    __slots__ = 'data', 'index', 'lowlink', 'onstack'

    def __init__(self, data):
        self.data = data
        self.index = -1
        self.lowlink = -1
        self.onstack = False


class _TarjanStronglyConnectedComponentsAlgorithm: # pylint: disable=R0903
    __slots__ = 'nodes', 'graph', 'last_index', 'stack', 'sccs'

    def _find(self, vertex1):
        vertex1.index = self.last_index
        vertex1.lowlink = self.last_index
        vertex1.onstack = True
        self.stack.append(vertex1)
        self.last_index += 1

        for vertex2_data in self.graph[vertex1.data]:
            vertex2 = self.nodes[vertex2_data]
            if vertex2.index == -1:
                self._find(vertex2)
                vertex1.lowlink = min(vertex1.lowlink, vertex2.lowlink)
            elif vertex2.onstack:
                vertex1.lowlink = min(vertex1.lowlink, vertex2.index)

        if vertex1.index == vertex1.lowlink:
            vertex2 = None
            scc = []

            while vertex1 != vertex2:
                vertex2 = self.stack.pop()
                vertex2.onstack = False
                scc.append(vertex2.data)

            if len(scc) > 1:
                self.sccs.append(scc)

    def find(self):
        for node in self.nodes.values():
            if node.index == -1:
                self._find(node)

        return self.sccs

    def __init__(self, nodes, graph):
        self.nodes = {node: _TarjanStronglyConnectedComponentsNode(node) for node in nodes}
        self.graph = graph
        self.last_index = 1
        self.stack = []
        self.sccs = []


class _GraphNodeOrderAlgorithm: # pylint: disable=R0903
    __slots__ = 'nodes', 'graph', 'order_f', 'order_b'

    def _get_order(self, vertex1):
        if self.order_f[vertex1] > 0:
            return self.order_f[vertex1]

        if not self.graph[vertex1]:
            return 1

        return max(self._get_order(vertex2) for vertex2 in self.graph[vertex1]) + 1

    def __init__(self, nodes, graph):
        from collections import defaultdict

        self.nodes = nodes
        self.graph = graph
        self.order_f = defaultdict(int)
        self.order_b = defaultdict(list)

    def find(self):
        for node in self.nodes:
            order = self._get_order(node)
            self.order_f[node] = order
            self.order_b[order].append(node)

        return self.order_b


class Orchestration: # pylint: disable=R0903
    __slots__ = 'configuration', 'brooms', 'middlewares', 'router', 'workers'

    def _create_object(self, object_factory, object_kwargs): # pylint: disable=R0201
        from inspect import _empty
        from inspect import _KEYWORD_ONLY
        from inspect import _POSITIONAL_ONLY
        from inspect import _POSITIONAL_OR_KEYWORD
        #from inspect import _VAR_KEYWORD
        #from inspect import _VAR_POSITIONAL
        from inspect import signature

        parameters = dict(signature(object_factory).parameters)
        args = []
        kwargs = {}

        for name, desc in parameters.items():
            value = object_kwargs.get(name)

            if (value is None) and (desc.default != _empty):
                value = desc.default

            if desc.kind == _KEYWORD_ONLY:
                kwargs[name] = value
            elif desc.kind == _POSITIONAL_ONLY:
                args.append(value)
            elif desc.kind == _POSITIONAL_OR_KEYWORD:
                args.append(value)
            #elif desc.kind == _VAR_KEYWORD:
            #    pass
            #elif desc.kind == _VAR_POSITIONAL:
            #    pass

        return object_factory(*args, **kwargs)

    def _init_brooms(self):
        def _get_root__package_name():
            from traceback import extract_stack
            from os.path import abspath

            stack = extract_stack()

            for frame in reversed(stack):
                if frame.name == '<module>':
                    return abspath(frame.filename)

            return abspath(stack[0].filename)

        root_package_name = _get_root__package_name()
        broom_confs = self.configuration.get('brooms', {})

        self.brooms = []

        for broom_name, broom_conf in broom_confs.items():
            self.brooms.append(Broom(root_package_name, broom_name, broom_conf))

    def _init_middlewares(self, middleware_kwargs):
        def _build_graph(brooms):
            from collections import defaultdict

            nodes = set()
            graph_f = defaultdict(set)
            graph_b = defaultdict(set)

            # Build graph of middleware classes.
            # 1) Each node is a single middleware class.
            # 2) Each edge is a pair of sequential middleware classes.

            for broom in brooms:
                for middleware_class in broom.middleware_classes:
                    nodes.add(middleware_class)

                if len(broom.middleware_classes) >= 2:
                    prev_middleware_class = broom.middleware_classes[0]

                    for next_middleware_class in broom.middleware_classes[1:]:
                        graph_f[prev_middleware_class].add(next_middleware_class)
                        graph_b[next_middleware_class].add(prev_middleware_class)
                        prev_middleware_class = next_middleware_class

            return nodes, graph_f, graph_b

        middleware_class_nodes, middleware_class_graph_f, middleware_class_graph_b = _build_graph(self.brooms)
        tarjan = _TarjanStronglyConnectedComponentsAlgorithm(middleware_class_nodes, middleware_class_graph_f)
        sccs = tarjan.find()

        if sccs:
            message = \
                'Cannot order middlewares in a way which satisfies expectations of all brooms:' + \
                ''.join(['\n' + ', '.join([f'{c.__module__}.{c.__name__}' for c in scc]) for scc in sccs])

            raise RuntimeError(message)

        graph_node_order = _GraphNodeOrderAlgorithm(middleware_class_nodes, middleware_class_graph_b)
        middleware_class_order = graph_node_order.find()

        self.middlewares = []

        for middleware_classes in middleware_class_order.values():
            for middleware_class in middleware_classes:
                self.middlewares.append(self._create_object(middleware_class, middleware_kwargs))

    def _init_routes(self, handler_kwargs, static_root):
        from broomhilda.extras.handlers.static import StaticHandler
        from broomhilda.extras.middlewares import RoutingMiddleware
        from broomhilda.extras.routes import Router
        from os.path import join

        self.router = Router()

        for broom in self.brooms:
            for handler_class, handler_paths in broom.handler_classes.items():
                handler = self._create_object(handler_class, handler_kwargs)

                for handler_path in handler_paths:
                    self.router.add(broom.prefix + handler_path, handler)

            for url_prefix, path_prefix in broom.statics.items():
                self.router.add(broom.prefix + url_prefix, StaticHandler(join(static_root, path_prefix)))

        self.middlewares.append(RoutingMiddleware(self.router))

    def _init_workers(self, worker_kwargs):
        worker_classes = set()

        self.workers = []

        for broom in self.brooms:
            for worker_class in broom.worker_classes:
                if not worker_class in worker_classes:
                    worker = self._create_object(worker_class, worker_kwargs)
                    self.workers.append(worker)
                    worker_classes.add(worker_class)

    def __init__(self, configuration, middleware_kwargs={}, handler_kwargs={}, static_root='.', worker_kwargs={}): # pylint: disable=R0913,W0102
        self.configuration = configuration
        self.brooms = None
        self.middlewares = None
        self.router = None
        self.workers = None
        self._init_brooms()
        self._init_middlewares(middleware_kwargs)
        self._init_routes(handler_kwargs, static_root)
        self._init_workers(worker_kwargs)
