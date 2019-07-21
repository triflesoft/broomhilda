#!/usr/bin/env python3

from datetime import date
from datetime import datetime
from datetime import timedelta
from jinja2 import ChoiceLoader
from jinja2 import Environment
from jinja2 import FileSystemLoader
from os.path import dirname
from os.path import join
from pprint import pprint

from broomhilda import BASE_PATH
from broomhilda.facade.server.server11 import Server11
from broomhilda.models.binders import BinderBase
from broomhilda.models.binders import CheckboxWidget
from broomhilda.models.binders import DateWidget
from broomhilda.models.binders import DateTimeWidget
from broomhilda.models.binders import EMailWidget
from broomhilda.models.binders import FileWidget
from broomhilda.models.binders import HiddenWidget
from broomhilda.models.binders import NumberWidget
from broomhilda.models.binders import PasswordWidget
from broomhilda.models.binders import RadioWidget
from broomhilda.models.binders import SearchWidget
from broomhilda.models.binders import SelectWidget
from broomhilda.models.binders import TextWidget
from broomhilda.models.binders import TimeWidget
from broomhilda.models.binders import UrlWidget
from broomhilda.extras.handlers.static import StaticHandler
from broomhilda.extras.handlers.template import Jinja2HandlerBase
from broomhilda.extras.handlers.template import get_builtin_jinja2_loader
from broomhilda.extras.handlers.template import jinja2_template
from broomhilda.extras.handlers.template import jinja2_template
from broomhilda.extras.middlewares import RoutingMiddleware
from broomhilda.extras.routes import Router
from unicodedata import name


class TestBinder(BinderBase):
    checkbox = CheckboxWidget(
        verbose_name='Test Checkbox',
        choices={None: 'Whatever', True: 'Enabled', False: 'Disabled'},
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)

    radio = RadioWidget(
        verbose_name='Test Radio',
        choices={'A': 'radio A', 'B': 'radio B', 'C': 'radio C'},
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)
    select = SelectWidget(
        verbose_name='Test Select',
        choices=dict(
                [('', 'NOTHING')] +
                [(c, name(c)) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz']),
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)

    date = DateWidget(
        min_value=(date.today() - timedelta(days=15)),
        max_value=(date.today() + timedelta(days=15)),
        verbose_name='Test Date Picker',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)
    datetime = DateTimeWidget(
        min_value=(datetime.now().replace(microsecond=0) - timedelta(days=15)),
        max_value=(datetime.now().replace(microsecond=0) + timedelta(days=15)),
        verbose_name='Test Date and Time Picker',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)
    time = TimeWidget(
        verbose_name='Test Time Picker',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)

    file = FileWidget(
        verbose_name='Test File',
        help_text="Some help text here to give user an advice.")

    number = NumberWidget(
        verbose_name='Test Number',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)

    email = EMailWidget(
        verbose_name='Test Email',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)
    hidden = HiddenWidget(
        verbose_name='Test Hidden',
        help_text="Some help text here to give user an advice.")
    password = PasswordWidget(
        verbose_name='Test Password',
        help_text="Some help text here to give user an advice.")
    search = SearchWidget(
        verbose_name='Test Search',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)
    text = TextWidget(
        verbose_name='Test Text',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)
    url = UrlWidget(
        verbose_name='Test Url',
        help_text="Some help text here to give user an advice.",
        can_list_filter=True)


class DefaultHandler(Jinja2HandlerBase):
    def __init__(self):
        # Jinja2HandlerBase.__init__ will perform all kinds of black magic.
        super().__init__(Environment(
            loader=ChoiceLoader([
                get_builtin_jinja2_loader(),
                FileSystemLoader(dirname(__file__))
            ]),
            # Always enable async.
            enable_async=True))

    @jinja2_template('test_binders_item.html')
    async def get(self, request, response):
        binder1 = TestBinder(prefix='post-1-')
        binder1._validate_item_select()
        binder2 = TestBinder(prefix='post-2-')
        binder2._validate_list_filter()

        return { 'binder1': binder1, 'binder2': binder2 }

    @jinja2_template('test_binders_item.html')
    async def post(self, request, response):
        data = await request.read_form()

        binder1 = TestBinder(prefix='post-1-')
        binder1._update(data)
        binder1._validate_item_update()

        binder2 = TestBinder(prefix='post-2-')
        binder2._update(data)
        binder2._validate_list_filter()

        print()
        print('========== item update result 1 ==========')
        pprint(binder1._result, width=160)
        print('========== item update errors 1 ==========')
        pprint(binder1._errors, width=160)
        print('========== list filter result 2 ==========')
        pprint(binder2._result, width=160)
        print('========== list filter errors 2 ==========')
        pprint(binder2._errors, width=160)
        print()

        return { 'binder1': binder1, 'binder2': binder2 }

router = Router()
router.add('/', DefaultHandler())
router.add('/static/<path:path>', StaticHandler(join(BASE_PATH, 'styles')))

# HTTP 1.1 server
server = Server11(
    middlewares=[RoutingMiddleware(router)],
    default_headers=(('Server', 'broomhilda-http-server/1.2.3.4'),))

print('Open the following URL with browser: http://localhost:8080/')

from webbrowser import open

open('http://localhost:8080/')

server.run(port=8080)
