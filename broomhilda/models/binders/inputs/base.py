class InputBase(object):
    def __init__(
        self,
        jinja2_module_name,
        jinja2_macro_name,
        attributes={},
        can_item_select=True,
        can_item_update=True,
        can_list_select=True,
        can_list_update=True,
        can_list_filter=False,
        can_list_search=False,
        can_list_sort=False,
        is_nullable=False,
        verbose_name=None,
        help_text=None,
        choices=None,
        default_item_update=None,
        default_list_update=None,
        default_list_filter=None):
        self.name = None
        self.jinja2_module_name = jinja2_module_name
        self.jinja2_macro_name = jinja2_macro_name
        self.attributes = attributes
        self.can_item_select = can_item_select
        self.can_item_update = can_item_update
        self.can_list_select = can_list_select
        self.can_list_update = can_list_update
        self.can_list_filter = can_list_filter
        self.can_list_search = can_list_search
        self.can_list_sort = can_list_sort
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.choices = choices
        self.default_item_update = default_item_update
        self.default_list_update = default_list_update
        self.default_list_filter = default_list_filter
        self._max_filter_length = 256


class NullableInputBase(InputBase):
    def __init__(
        self,
        jinja2_module_name,
        jinja2_macro_name,
        is_nullable=False,
        default_item_update=None,
        default_list_update=None,
        default_list_filter=None,
        **kwargs):
        super().__init__(
            jinja2_module_name,
            jinja2_macro_name,
            default_item_update=default_item_update,
            default_list_update=default_list_update,
            **kwargs)
        self.is_nullable = is_nullable
