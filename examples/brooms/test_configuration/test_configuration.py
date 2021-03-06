#!/usr/bin/env python3

from os.path import dirname
from os.path import join
from pprint import pprint

from broomhilda.brooms.configuration import Configuration

base_path = dirname(__file__)

configuration = Configuration([
    join(base_path, './level-01'),
    join(base_path, './level-02'),
    join(base_path, './level-03'),
])

pprint(configuration.data)
