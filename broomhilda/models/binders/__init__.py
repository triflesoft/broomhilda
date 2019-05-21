from inspect import isclass

from broomhilda.models.binders.inputs.base import InputBase
from broomhilda.models.binders.inputs.bool import CheckboxInput
from broomhilda.models.binders.inputs.choice import RadioInput
from broomhilda.models.binders.inputs.choice import SelectInput
from broomhilda.models.binders.inputs.date import DateInput
from broomhilda.models.binders.inputs.date import DateTimeInput
from broomhilda.models.binders.inputs.date import TimeInput
from broomhilda.models.binders.inputs.file import FileInput
from broomhilda.models.binders.inputs.number import NumberInput
from broomhilda.models.binders.inputs.text import EMailInput
from broomhilda.models.binders.inputs.text import EMailInput
from broomhilda.models.binders.inputs.text import HiddenInput
from broomhilda.models.binders.inputs.text import PasswordInput
from broomhilda.models.binders.inputs.text import SearchInput
from broomhilda.models.binders.inputs.text import TextInput
from broomhilda.models.binders.inputs.text import UrlInput


class InputProxy(object):
    def __getattr__(self, name):
        return getattr(self._input, name)

    def __init__(self, form, input):
        self._form = form
        self._input = input

    def _validate_item_select(self):
        result, _ = self._input._validate_item_update(self._form._raw_data)

        self._form._result[self._input.name] = result
        self._form._errors[self._input.name] = {}

    def _validate_item_update(self):
        result, errors = self._input._validate_item_update(self._form._raw_data)

        self._form._result[self._input.name] = result
        self._form._errors[self._input.name] = errors

        return len(errors) == 0

    def _validate_list_filter(self):
        result, errors = self._input._validate_list_filter(self._form._raw_data)

        self._form._result[self._input.name] = result
        self._form._errors[self._input.name] = errors

        return len(errors) == 0

    def is_valid(self, item):
        return self._form._is_validated and len(self.item_errors(item)) == 0

    def is_invalid(self, item):
        return self._form._is_validated and len(self.item_errors(item)) > 0

    def item_value(self, item):
        value = self._form._result.get(self._input.name)

        if value is None:
            return None

        return value.get(item)

    def item_format(self, item, format=None):
        value = self.item_value(item)

        if value is None:
            return ''

        if format is None:
            return str(value)

        return value.__format__(format)

    def item_errors(self, item):
        input_errors = self._form._errors.get(self._input.name, None)

        if input_errors is None:
            return []

        return input_errors.get(item, [])


class BinderMeta(object):
    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs


class BinderBase(object):
    def __new__(cls, *args, **kwargs):
        meta_dict = {}
        input_dict = {}

        for base in reversed(cls.__mro__):
            meta_class = getattr(base, 'Meta', None)

            if meta_class and isclass(meta_class):
                for name in dir(meta_class):
                    if not name.startswith('_'):
                        meta_dict[name] = getattr(meta_class, name)

            for name, input in base.__dict__.items():
                if not name.startswith('_'):
                    if not input.name:
                        input.name = name

                    if isinstance(input, InputBase):
                        input_dict[input.name] = input

        result = super().__new__(cls)
        result._meta = BinderMeta(list(input_dict.values()), meta_dict)

        return result

    def __init__(self, prefix='', **kwargs):
        self._prefix = prefix
        self._raw_data = {}
        self._is_validated = False
        self._is_valid = False
        self._result = {}
        self._errors = {}
        self._inputs = []
        self._update(kwargs)

        for inp in self._meta.inputs:
            proxy = InputProxy(self, inp)
            self._inputs.append(proxy)
            setattr(self, inp.name, proxy)

    def _update(self, data):
        self._raw_data = {}
        self._is_validated = False

        for name, value in data.items():
            if name.startswith(self._prefix):
                self._raw_data[name[len(self._prefix):]] = value

    def _validate_item_select(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for inp in self._inputs:
            inp._validate_item_select()

    def _validate_item_update(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for inp in self._inputs:
            if not inp._validate_item_update():
                self._is_valid = False

        return self._is_valid

    def _validate_list_filter(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for inp in self._inputs:
            if not inp._validate_list_filter():
                self._is_valid = False

        return self._is_valid

    def _get_list_layout(self, request):
        pass

    def _get_item_layout(self, request):
        pass
