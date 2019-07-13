class Broom:
    def _import_identifier(self, name):
        from importlib import import_module

        if '.' in name:
            module_name, function_name = name.rsplit('.', 1)
            module = import_module(module_name, package=self.module.__name__)

            return getattr(module, function_name)
        else:
            return getattr(self.module, name)

    def __init__(self, root_package, global_context, name, configuration):
        from importlib import import_module
        from inspect import signature
        from os.path import abspath

        self.name = name
        self.module = import_module(self.name, package=root_package)
        self.middlewares = []

        for middleware_name in configuration.get('middlewares', []):
            middleware_class = self._import_identifier(middleware_name)
            parameters = dict(signature(middleware_class).parameters)

            if len(parameters) == 0:
                middleware = self._import_identifier(middleware_name)()
            elif len(parameters) == 1:
                middleware = self._import_identifier(middleware_name)(global_context)
            else:
                raise Exception()

            self.middlewares.append(middleware)

        pass

        """
        self.routes = configuration.get('routes', {})
        self.tasks = configuration.get('tasks', {})"""


def serve(configuration, global_context={}):
    from broomhilda.extras.middlewares import RoutingMiddleware
    from broomhilda.extras.routes import Router
    from broomhilda.facade.server.server11 import Server11
    from importlib import import_module
    from traceback import extract_stack
    from os.path import abspath

    from pprint import pprint

    stack = extract_stack()
    root_package = ''

    for frame in reversed(stack):
        if frame.name == '<module>':
            root_package = abspath(frame.filename)
            break

    brooms = configuration.get('brooms', {})

    for broom_name, broom_conf in brooms.items():
        broom = Broom(root_package, global_context, broom_name, broom_conf)

    pprint(configuration)
