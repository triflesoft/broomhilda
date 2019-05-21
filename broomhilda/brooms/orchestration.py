from collections import namedtuple
from importlib import import_module

from broomhilda.brooms.configuration import load

from pprint import pprint


class Broom(object):
    def __init__(self, name, configuration):
        self._name = name
        self._assets = {}
        self._middlewares = {}
        self._options = {}
        self._routes = {}
        self._tasks = {}
        self._module = None
        self._object = None


class Server(object):
    def __init__(self, configuration_paths):
        pass

    def run(self):
        pass


async def _serve(configuration_paths):
    configuration = load(configuration_paths)
    brooms = configuration.get('brooms', {})
    endpoints = configuration.get('endpoints', [])


    for item_name, item_data in brooms.items():
        item_root_module = import_module(item_name)
        item_broom_module = import_module('.broom', item_root_module.__package__)
        item_broom_class = getattr(item_broom_module, 'Broom')
        item_broom = item_broom_class(**item_data.get('options', {}))
        print(item_root_module)
        print(item_broom_module)
        pprint(item_data)


    # pprint(configuration, compact=False)

    async with TaskGroup() as task_group:
        pass
        #await task_group.spawn(additional_coroutine)

        # server = Server11(
        #     middlewares=[RoutingMiddleware(router)],
        #     default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))
        # task_group.spawn(server.run(port=8080))

def serve(configuration_paths):
    run(_serve(configuration_paths))
