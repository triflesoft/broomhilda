# Required for reimport
from broomhilda.models.binders.widgets.base import WidgetBase
from broomhilda.models.binders.widgets.bool import CheckboxWidget
from broomhilda.models.binders.widgets.choice import RadioWidget
from broomhilda.models.binders.widgets.choice import SelectWidget
from broomhilda.models.binders.widgets.date import DateWidget
from broomhilda.models.binders.widgets.date import DateTimeWidget
from broomhilda.models.binders.widgets.date import TimeWidget
from broomhilda.models.binders.widgets.file import FileWidget
from broomhilda.models.binders.widgets.number import NumberWidget
from broomhilda.models.binders.widgets.text import EMailWidget
from broomhilda.models.binders.widgets.text import HiddenWidget
from broomhilda.models.binders.widgets.text import PasswordWidget
from broomhilda.models.binders.widgets.text import SearchWidget
from broomhilda.models.binders.widgets.text import TextWidget
from broomhilda.models.binders.widgets.text import UrlWidget


__all__ = [
    'WidgetBase',
    'CheckboxWidget',
    'RadioWidget',
    'SelectWidget',
    'DateWidget',
    'DateTimeWidget',
    'TimeWidget',
    'FileWidget',
    'NumberWidget',
    'EMailWidget',
    'HiddenWidget',
    'PasswordWidget',
    'SearchWidget',
    'TextWidget',
    'UrlWidget',
    'WidgetProxy'
]


class WidgetProxy:
    def __getattr__(self, name):
        return getattr(self._widget, name)

    def __init__(self, form, widget):
        self._form = form
        self._widget = widget

    def _validate_item_select(self):
        result, _ = self._widget._validate_item_update(self._form._raw_data)  # pylint: disable=W0212

        self._form._result[self._widget.name] = result  # pylint: disable=W0212
        self._form._errors[self._widget.name] = {}  # pylint: disable=W0212

    def _validate_item_update(self):
        result, errors = self._widget._validate_item_update(self._form._raw_data)  # pylint: disable=W0212

        self._form._result[self._widget.name] = result  # pylint: disable=W0212
        self._form._errors[self._widget.name] = errors  # pylint: disable=W0212

        return len(errors) == 0

    def _validate_list_filter(self):
        result, errors = self._widget._validate_list_filter(self._form._raw_data)  # pylint: disable=W0212

        self._form._result[self._widget.name] = result  # pylint: disable=W0212
        self._form._errors[self._widget.name] = errors  # pylint: disable=W0212

        return len(errors) == 0

    def is_valid(self, item):
        return self._form._is_validated and len(self.item_errors(item)) == 0  # pylint: disable=W0212

    def is_invalid(self, item):
        return self._form._is_validated and len(self.item_errors(item)) > 0  # pylint: disable=W0212

    def item_value(self, item):
        value = self._form._result.get(self._widget.name)  # pylint: disable=W0212

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
        widget_errors = self._form._errors.get(self._widget.name, None)  # pylint: disable=W0212

        if widget_errors is None:
            return []

        return widget_errors.get(item, [])


class BinderMeta:  # pylint: disable=R0903
    def __init__(self, widgets, *args, **kwargs):
        self.widgets = widgets


class BinderBase:  # pylint: disable=R0902,R0903
    def __new__(cls, *args, **kwargs):
        from inspect import isclass

        meta_dict = {}
        widget_dict = {}

        for base in reversed(cls.__mro__):
            meta_class = getattr(base, 'Meta', None)

            if meta_class and isclass(meta_class):
                for name in dir(meta_class):
                    if not name.startswith('_'):
                        meta_dict[name] = getattr(meta_class, name)

            for name, widget in base.__dict__.items():
                if not name.startswith('_'):
                    if not widget.name:
                        widget.name = name

                    if isinstance(widget, WidgetBase):
                        widget_dict[widget.name] = widget

        result = super().__new__(cls)
        result._meta = BinderMeta(list(widget_dict.values()), meta_dict)  # pylint: disable=W0212

        return result

    def __init__(self, prefix='', **kwargs):
        self._prefix = prefix
        self._raw_data = {}
        self._is_validated = False
        self._is_valid = False
        self._result = {}
        self._errors = {}
        self._data = {}
        self._widgets = []
        self._update(kwargs)

        for widget in self._meta.widgets:  # pylint: disable=E1101
            proxy = WidgetProxy(self, widget)
            self._widgets.append(proxy)
            setattr(self, widget.name, proxy)

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

        for widget in self._widgets:
            widget._validate_item_select()  # pylint: disable=W0212

    def _validate_item_update(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for widget in self._widgets:
            if not widget._validate_item_update():  # pylint: disable=W0212
                self._is_valid = False

        return self._is_valid

    def _validate_list_filter(self):
        self._is_validated = True
        self._errors = {}
        self._data = {}
        self._is_valid = True

        for widget in self._widgets:
            if not widget._validate_list_filter():  # pylint: disable=W0212
                self._is_valid = False

        return self._is_valid

    def _get_list_layout(self, request):
        pass

    def _get_item_layout(self, request):
        pass
