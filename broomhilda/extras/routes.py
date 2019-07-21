class Route:
    def _add_parameter_converter(self, match):
        from uuid import UUID

        name = match.group('name')
        pattern = match.group('pattern')
        converter = str

        if pattern is None or pattern == 'str':
            pattern = '[^/]+'
        elif pattern == 'slug':
            pattern = '[A-Za-z0-9-_]+'
        elif pattern == 'path':
            pattern = '.*'
        elif pattern == 'int':
            pattern = '\\d+'
            converter = int
        elif pattern == 'uuid':
            pattern = '(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(?:[0-9a-fA-F]{32})'
            converter = UUID

        self.parameter_converters[name] = converter

        return f'(?P<{name}>{pattern})'

    def _add_parameter_identifier(self, match): # pylint: disable=R0201
        pattern = match.group('pattern')

        if pattern is None or pattern == '[^/]+':
            pattern = 'str'
        elif pattern == '.+':
            pattern = 'path'
        elif pattern == '\\d+':
            pattern = 'int'

        return f'<{pattern}>'

    def _add_parameter_signature(self, match): # pylint: disable=R0201
        name = match.group('name')

        return f'<{name}>'

    def __init__(self, path_pattern, method_handlers):
        from inspect import iscoroutinefunction
        from re import compile as re_compile

        self.method_handlers = {}

        for name, handler in method_handlers.items():
            if not iscoroutinefunction(handler):
                raise RuntimeError(f'Handler "{handler}" must be async function or async method.')

            self.method_handlers[name] = handler

        url_parameter_pattern = re_compile(r'<(?P<name>[A-Za-z0-9_]+?)(?:\:(?P<pattern>.+?))?>')

        self.parameter_converters = {}
        self.path_pattern = path_pattern
        self.path_regexp = re_compile(url_parameter_pattern.sub(self._add_parameter_converter, path_pattern))
        self.identifier = url_parameter_pattern.sub(self._add_parameter_identifier, path_pattern)
        self.signature = url_parameter_pattern.sub(self._add_parameter_signature, path_pattern)

    def match(self, path, method_name):
        match = self.path_regexp.fullmatch(path)

        if not match:
            return 404, None, None

        handler = self.method_handlers.get(method_name)

        if handler is None:
            return 405, None, None

        path_parameters = {}

        for name, converter in self.parameter_converters.items():
            path_parameters[name] = converter(match.group(name))

        return 200, handler, path_parameters

    def merge(self, new_route):
        self.method_handlers.update(new_route.method_handlers)


class Router:
    def __init__(self):
        self.routes = {}

    def _add_functions(self, path_pattern, method_handlers):
        new_route = Route(path_pattern, method_handlers)
        old_route = self.routes.get(new_route.identifier)

        if old_route:
            if old_route.signature != new_route.signature:
                raise RuntimeError(f'Parameter name differs between patterns of same signature "{old_route.path_pattern}" and "{new_route.path_pattern}".')

            old_route.merge(new_route)
        else:
            self.routes[new_route.identifier] = new_route

    def _add_object(self, path_pattern, handler, method_names):
        method_handlers = {}

        for method_name in method_names:
            method_handler = getattr(handler, method_name, None)

            if method_handler:
                if not callable(method_handler):
                    raise RuntimeError(f'Handler "{method_handler}" must be async method.')

                method_handlers[method_name] = method_handler

        self._add_functions(path_pattern, method_handlers)

    def add(self, path_pattern, handler, method_names=('connect', 'delete', 'get', 'head', 'options', 'patch', 'post', 'put', 'trace')):
        from inspect import isfunction

        if isinstance(method_names, str):
            method_names = (method_names,)

        method_names = frozenset(method_name.lower() for method_name in method_names)

        if isinstance(handler, Router):
            for route in handler.routes.values():
                method_handlers = {}

                for method_name, method_handler in route.method_handlers.items():
                    if method_name in method_names:
                        method_handlers[method_name] = method_handler

                if path_pattern.endswith('/'):
                    self._add_functions(path_pattern + route.path_pattern.lstrip('/'), method_handlers)
                else:
                    self._add_functions(path_pattern + route.path_pattern, method_handlers)
        else:
            if isfunction(handler):
                self._add_functions(path_pattern, {method_name: handler for method_name in method_names})
            else:
                self._add_object(path_pattern, handler, method_names)

    def match(self, path, method_name):
        method_name = method_name.lower()
        final_result = 404
        final_handler = None
        final_parameters = None

        for route in self.routes.values():
            result, handler, parameters = route.match(path, method_name)

            if result < 300:
                final_result = result
                final_handler = handler
                final_parameters = parameters
                break
            elif result == 405:
                final_result = result
                final_handler = None
                final_parameters = None
                break

        return final_result, final_handler, final_parameters
