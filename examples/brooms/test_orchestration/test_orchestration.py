#!/usr/bin/env python3

from os.path import dirname

from broomhilda.brooms.configuration import load

base_path = dirname(__file__)
print(base_path)

configuration = load([base_path,])

from pprint import pprint
pprint(configuration)

