__all__ = ['Configuration']


class _ConfigurationFile:
    __slots__ = 'absolute_path', 'relative_path', 'size', 'atime', 'mtime', 'ctime'

    def __init__(self, absolute_path, relative_path, size, atime, mtime, ctime):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.size = size
        self.atime = atime
        self.mtime = mtime
        self.ctime = ctime

    def read(self):
        from json import load as json_load
        from yaml import safe_load as yaml_load

        # Any meaningful config file is larger than 4 bytes
        # So we filter out empty files or files with single \r\n
        if self.size > 4:
            if self.absolute_path.endswith('.json'):
                with open(self.absolute_path, 'r') as file:
                    return json_load(file)
            elif self.absolute_path.endswith('.yaml'):
                with open(self.absolute_path, 'r') as file:
                    return yaml_load(file)

        return None


class _ConfigurationLayer:
    def _scan_(self, absolute_path, relative_path):
        from os import scandir
        from os.path import join

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
            self.file_entries.append(
                _ConfigurationFile(
                    entry_absolute_path,
                    entry_relative_path,
                    stat.st_size,
                    stat.st_atime,
                    stat.st_mtime,
                    stat.st_ctime))

        for entry in directory_entries:
            entry_absolute_path = join(absolute_path, entry.name)
            entry_relative_path = join(relative_path, entry.name)
            self._scan_(entry_absolute_path, entry_relative_path)

    def __init__(self, absolute_path):
        from os.path import abspath

        self.absolute_path = absolute_path
        self.file_entries = []
        self._scan_(abspath( self.absolute_path), '')


class Configuration:
    def _merge_dict(self, lower_dict):
        def _merge_dict_recursive(upper_dict, upper_dict_priority, lower_dict, lower_dict_priority):
            for item_key, lower_item in lower_dict.items():
                upper_item = upper_dict.get(item_key)

                if (type(lower_item) is dict) and (type(upper_item) is dict):
                    should_reset = False

                    for key, value in upper_item.items():
                        if (key is None) and (value is None):
                            should_reset = True
                        break

                    if should_reset:
                        del upper_item[None]
                    else:
                        upper_item_priority = upper_item.get('__priority', upper_dict_priority)
                        lower_item_priority = lower_item.get('__priority', lower_dict_priority)
                        _merge_dict_recursive(upper_item, upper_item_priority, lower_item, lower_item_priority)
                elif (type(lower_item) is list) and (type(upper_item) is list):
                    if upper_item:
                        if upper_item[0] is None:
                            upper_dict[item_key] = upper_item[1:]
                        else:
                            upper_dict[item_key] = lower_item + upper_item
                else:
                    if upper_dict_priority < lower_dict_priority:
                        upper_dict[item_key] = lower_item
                    else:
                        if not item_key in upper_dict:
                            upper_dict[item_key] = lower_item

        _merge_dict_recursive(self.data, 0, lower_dict, 0)

    def _clear_dict(self):
        def _clear_dict_recursive(dirty_dict):
            for key in [k for k in dirty_dict.keys() if (type(k) is str) and k.startswith('__')]:
                del dirty_dict[key]

            for key, item in dirty_dict.items():
                if type(item) is dict:
                    _clear_dict_recursive(item)

        _clear_dict_recursive(self.data)

    def __init__(self, configuration_paths):
        from collections import defaultdict

        layers = []

        for configuration_path in configuration_paths:
            layers.append(_ConfigurationLayer(configuration_path))

        file_data = defaultdict(list)
        file_skip = set()

        for layer in reversed(layers):
            for file_entry in layer.file_entries:
                if not file_entry.relative_path in file_skip:
                    file_datum = file_entry.read()

                    if type(file_datum) is dict:
                        file_data[file_entry.relative_path].append(file_datum)
                    else:
                        file_skip.add(file_entry.relative_path)

        self.data = {}

        for file_data in reversed(list(file_data.values())):
            for file_datum in file_data:
                self._merge_dict(file_datum)

        self._clear_dict()

    def __getitem__(self, key):
        return self.data.get(key)

    def get(self, key, default=None):
        return self.data.get(key, default)
