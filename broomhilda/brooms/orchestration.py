class Broom:
    def _import_identifier(self, name):
        from importlib import import_module

        if '.' in name:
            module_name, function_name = name.rsplit('.', 1)
            module = import_module(module_name, package=self.module.__name__)

            return getattr(module, function_name)
        else:
            return getattr(self.module, name)

    def __init__(self, root_package, name, configuration):
        from importlib import import_module
        from os.path import abspath

        self.name = name
        self.module = import_module(self.name, package=root_package)
        self.middleware_classes = []

        for middleware_name in configuration.get('middlewares', []):
            self.middleware_classes.append(self._import_identifier(middleware_name))

        """
        self.routes = configuration.get('routes', {})
        self.tasks = configuration.get('tasks', {})"""


class _TarjanStronglyConnectedComponentsNode:
    __slots__ = 'data', 'index', 'lowlink', 'onstack'

    def __init__(self, data):
        self.data = data
        self.index = -1
        self.lowlink = -1
        self.onstack = False


class _TarjanStronglyConnectedComponentsAlgorithm:
    def __init__(self, nodes, graph):
        self.nodes = { node: _TarjanStronglyConnectedComponentsNode(node) for node in nodes }
        self.graph = graph
        self.last_index = 1
        self.stack = []
        self.sccs = []

    def _find(self, v):
        v.index = self.last_index
        v.lowlink = self.last_index
        v.onstack = True
        self.stack.append(v)
        self.last_index += 1

        for w_data in self.graph[v.data]:
            w = self.nodes[w_data]
            if w.index == -1:
                self._find(w)
                v.lowlink = min(v.lowlink, w.lowlink)
            elif w.onstack:
                v.lowlink = min(v.lowlink, w.index)

        if v.index == v.lowlink:
            w = None
            scc = []

            while v != w:
                w = self.stack.pop()
                w.onstack = False
                scc.append(w.data)

            if len(scc) > 1:
                self.sccs.append(scc)

    def find(self):
        for node in self.nodes.values():
            if node.index == -1:
                self._find(node)

        return self.sccs


class _GraphNodeOrderAlgorithm:
    def _get_order(self, v):
        if self.order_f[v] > 0:
            return self.order_f[v]

        if len(self.graph[v]) == 0:
            return 1

        return max(self._get_order(w) for w in self.graph[v]) + 1

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


class Orchestration:
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

        def _create_middleware(middleware_class, middleware_kwargs):
            from inspect import _empty
            from inspect import _KEYWORD_ONLY
            from inspect import _POSITIONAL_ONLY
            from inspect import _POSITIONAL_OR_KEYWORD
            from inspect import _VAR_KEYWORD
            from inspect import _VAR_POSITIONAL
            from inspect import signature

            parameters = dict(signature(middleware_class).parameters)
            args = []
            kwargs = {}

            for name, desc in parameters.items():
                value = middleware_kwargs.get(name)

                if (value is None) and (desc.default != _empty):
                    value = desc.default

                if desc.kind == _KEYWORD_ONLY:
                    kwargs[name] = value
                elif desc.kind == _POSITIONAL_ONLY:
                    args.append(value)
                elif desc.kind == _POSITIONAL_OR_KEYWORD:
                    args.append(value)
                elif desc.kind == _VAR_KEYWORD:
                    pass
                elif desc.kind == _VAR_POSITIONAL:
                    pass

            return middleware_class(*args, **kwargs)


        middleware_class_nodes, middleware_class_graph_f, middleware_class_graph_b = _build_graph(self.brooms)
        tarjan = _TarjanStronglyConnectedComponentsAlgorithm(middleware_class_nodes, middleware_class_graph_f)
        sccs = tarjan.find()

        if sccs:
            message = \
                'Cannot order middlewares in a way which satisfies expectations of all brooms:' + \
                ''.join(['\n' + ', '.join([f'{c.__module__}.{c.__name__}' for c in scc]) for scc in sccs])

            raise RuntimeError(message)

        graphNodeOrder = _GraphNodeOrderAlgorithm(middleware_class_nodes, middleware_class_graph_b)
        middleware_class_order = graphNodeOrder.find()

        for middleware_classes in middleware_class_order.values():
            for middleware_class in middleware_classes:
                self.middlewares.append(_create_middleware(middleware_class, middleware_kwargs))

    def __init__(self, configuration, middleware_kwargs={}, handler_kwargs={}):
        self.configuration = configuration
        self.brooms = []
        self.middlewares = []
        self._init_brooms()
        self._init_middlewares(middleware_kwargs)
