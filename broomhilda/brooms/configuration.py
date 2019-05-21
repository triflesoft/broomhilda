from collections import defaultdict
from collections import namedtuple
from json import load as json_load
from os import scandir
from os.path import abspath
from os.path import join
from yaml import safe_load as yaml_load


_FileEntry = namedtuple('_FileEntry', ('absolute_path', 'relative_path', 'size', 'atime', 'mtime', 'ctime'))


def _scandir_recursive(entries, absolute_path, relative_path):
    directory_entries = []
    file_entries = []

    for entry in scandir(absolute_path):
        if entry.is_dir():
            directory_entries.append(entry)
        elif entry.is_file():
            file_entries.append(entry)

    file_entries = sorted(file_entries, key=lambda e: e.name)
    directory_entries = sorted(directory_entries, key=lambda e: e.name)

    for entry in file_entries:
        entry_absolute_path = join(absolute_path, entry.name)
        entry_relative_path = join(relative_path, entry.name)

        stat = entry.stat()
        entries.append(
            _FileEntry(
                entry_absolute_path,
                entry_relative_path,
                stat.st_size,
                stat.st_atime,
                stat.st_mtime,
                stat.st_ctime))

    for entry in directory_entries:
        entry_absolute_path = join(absolute_path, entry.name)
        entry_relative_path = join(relative_path, entry.name)
        _scandir_recursive(entries, entry_absolute_path, entry_relative_path)


def _merge_dict(upper_dict, upper_dict_priority, lower_dict, lower_dict_priority):
    if upper_dict_priority < lower_dict_priority:
        for item_key, lower_item in lower_dict.items():
            upper_item = upper_dict.get(item_key)

            if (type(lower_item) is dict) and (type(upper_item) is dict):
                upper_item_priority = upper_item.get('__priority', upper_dict_priority)
                lower_item_priority = lower_item.get('__priority', lower_dict_priority)
                _merge_dict(upper_item, upper_item_priority, lower_item, lower_item_priority)
            elif (type(lower_item) is list) and (type(upper_item) is list):
                upper_dict[item_key] = lower_item + upper_item
            else:
                upper_dict[item_key] = lower_item
    else:
        for item_key, lower_item in lower_dict.items():
            upper_item = upper_dict.get(item_key)

            if (type(lower_item) is dict) and (type(upper_item) is dict):
                upper_item_priority = upper_item.get('__priority', upper_dict_priority)
                lower_item_priority = lower_item.get('__priority', lower_dict_priority)
                _merge_dict(upper_item, upper_item_priority, lower_item, lower_item_priority)
            elif (type(lower_item) is list) and (type(upper_item) is list):
                upper_dict[item_key] = lower_item + upper_item
            else:
                if not item_key in upper_dict:
                    upper_dict[item_key] = lower_item


def _clear_dict(dirty_dict):
    for key in [k for k in dirty_dict.keys() if (type(k) is str) and k.startswith('__')]:
        del dirty_dict[key]

    for key, item in dirty_dict.items():
        if type(item) is dict:
            _clear_dict(item)


def load(paths):
    layers = []
    file_data = defaultdict(dict)
    file_skip = set()

    for path in paths:
        entries = []

        _scandir_recursive(entries, abspath(path), '')

        layers.append(entries)

    for layer in reversed(layers):
        for file_entry in layer:
            if not file_entry.relative_path in file_skip:
                upper_data = file_data[file_entry.relative_path]

                if file_entry.size <= 4:
                    file_skip.add(file_entry.relative_path)
                else:
                    if file_entry.absolute_path.endswith('.json'):
                        with open(file_entry.absolute_path, 'r') as file:
                            lower_data = json_load(file)
                    elif file_entry.absolute_path.endswith('.yaml'):
                        with open(file_entry.absolute_path, 'r') as file:
                            lower_data = yaml_load(file)
                    else:
                        lower_data = None

                    if type(lower_data) is dict:
                        _merge_dict(upper_data, 0, lower_data, 0)

    result = {}

    for file_result in reversed(list(file_data.values())):
        _merge_dict(result, 0, file_result, 0)

    _clear_dict(result)

    return result
