# Required for reimport
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
from broomhilda.models.binders.inputs.text import HiddenInput
from broomhilda.models.binders.inputs.text import PasswordInput
from broomhilda.models.binders.inputs.text import SearchInput
from broomhilda.models.binders.inputs.text import TextInput
from broomhilda.models.binders.inputs.text import UrlInput


__all__ = [
    'InputBase',
    'CheckboxInput',
    'RadioInput',
    'SelectInput',
    'DateInput',
    'DateTimeInput',
    'TimeInput',
    'FileInput',
    'NumberInput',
    'EMailInput',
    'HiddenInput',
    'PasswordInput',
    'SearchInput',
    'TextInput',
    'UrlInput',
    'InputProxy'
]


class InputProxy:
    def __getattr__(self, name):
        return getattr(self._input, name)

    def __init__(self, form, input_):
        self._form = form
        self._input = input_

    def _validate_item_select(self):
        result, _ = self._input._validate_item_update(self._form._raw_data) # pylint: disable=W0212

        self._form._result[self._input.name] = result # pylint: disable=W0212
        self._form._errors[self._input.name] = {} # pylint: disable=W0212

    def _validate_item_update(self):
        result, errors = self._input._validate_item_update(self._form._raw_data) # pylint: disable=W0212

        self._form._result[self._input.name] = result # pylint: disable=W0212
        self._form._errors[self._input.name] = errors # pylint: disable=W0212

        return len(errors) == 0

    def _validate_list_filter(self):
        result, errors = self._input._validate_list_filter(self._form._raw_data) # pylint: disable=W0212

        self._form._result[self._input.name] = result # pylint: disable=W0212
        self._form._errors[self._input.name] = errors # pylint: disable=W0212

        return len(errors) == 0

    def is_valid(self, item):
        return self._form._is_validated and len(self.item_errors(item)) == 0 # pylint: disable=W0212

    def is_invalid(self, item):
        return self._form._is_validated and len(self.item_errors(item)) > 0 # pylint: disable=W0212

    def item_value(self, item):
        value = self._form._result.get(self._input.name) # pylint: disable=W0212

        if value is None:
            return None

        return value.get(item)

    def item_format(self, item, item_format=None):
        value = self.item_value(item)

        if value is None:
            return ''

        if item_format is None:
            return str(value)

        return value.__format__(item_format)

    def item_errors(self, item):
        input_errors = self._form._errors.get(self._input.name, None) # pylint: disable=W0212

        if input_errors is None:
            return []

        return input_errors.get(item, [])


class BinderMeta: # pylint: disable=R0903
    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs


class BinderBase: # pylint: disable=R0902,R0903
    def __new__(cls, *args, **kwargs):
        from inspect import isclass

        meta_dict = {}
        input_dict = {}

        for base in reversed(cls.__mro__):
            meta_class = getattr(base, 'Meta', None)

            if meta_class and isclass(meta_class):
                for name in dir(meta_class):
                    if not name.startswith('_'):
                        meta_dict[name] = getattr(meta_class, name)

            for name, input_ in base.__dict__.items():
                if not name.startswith('_'):
                    if not input_.name:
                        input_.name = name

                    if isinstance(input_, InputBase):
                        input_dict[input_.name] = input_

        result = super().__new__(cls)
        result._meta = BinderMeta(list(input_dict.values()), meta_dict) # pylint: disable=W0212

        return result

    def __init__(self, prefix='', **kwargs):
        self._prefix = prefix
        self._raw_data = {}
        self._is_validated = False
        self._is_valid = False
        self._result = {}
        self._errors = {}
        self._data = {}
        self._inputs = []
        self._update(kwargs)

        for inp in self._meta.inputs: # pylint: disable=E1101
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

        for input_ in self._inputs:
            input_._validate_item_select() # pylint: disable=W0212

    def _validate_item_update(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for input_ in self._inputs:
            if not input_._validate_item_update(): # pylint: disable=W0212
                self._is_valid = False

        return self._is_valid

    def _validate_list_filter(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for inp in self._inputs:
            if not inp._validate_list_filter(): # pylint: disable=W0212
                self._is_valid = False

        return self._is_valid

    def _get_list_layout(self, request):
        pass

    def _get_item_layout(self, request):
        pass
