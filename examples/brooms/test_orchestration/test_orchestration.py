#!/usr/bin/env python3

from os.path import dirname
from os.path import join
from pprint import pprint

from broomhilda.brooms.configuration import Configuration
from broomhilda.brooms.orchestration import Orchestration

base_path = dirname(__file__)

configuration = Configuration([
    join(base_path, '.'),
])

pprint(configuration.data)

orchestration = Orchestration(configuration)
