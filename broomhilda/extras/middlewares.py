from inspect import getsourcefile
from inspect import getsourcelines
from inspect import signature
from jinja2 import Environment
from jinja2 import FileSystemLoader
from os.path import dirname
from os.path import join
from os.path import normpath
from sys import exc_info
from traceback import format_exc


class RoutingMiddleware:
    def __init__(self, router, template_search_paths=None):
        if template_search_paths is None:
            template_search_paths = [normpath(join(dirname(__file__), '../styles/themes/default/'))]

        self._router = router
        self._environment = Environment(
            loader=FileSystemLoader(template_search_paths),
            enable_async=True,
            cache_size=0,
            autoescape=True)

    async def before(self, request, response):
        if not response._are_headers_sent:
            match_result, match_handler, match_parameters = self._router.match(request.path, request.method)

            if match_result >= 500:
                response.status_code = match_result
                await self.on_5xx_error(request, response, match_handler)
            elif match_result >= 400:
                response.status_code = match_result
                await self.on_4xx_error(request, response)
            else:
                try:
                    response.status_code = 200
                    await match_handler(request, response, **match_parameters)
                except:
                    if not response._are_headers_sent:
                        response.status_code = 500
                        await self.on_5xx_error(request, response, match_handler)


    async def after(self, request, response):
        pass

    async def on_4xx_error(self, request, response):
        template = self._environment.get_template('error-4xx.html')
        html = await template.render_async({
            'status_code': response.status_code,
            'status_text': response.status_text,
            'method': request.method,
            'path': request.raw_path.decode('ascii')
        })

        await response.send_html(html)

    async def on_5xx_error(self, request, response, handler):
        source_file = getsourcefile(handler)
        source_lines = getsourcelines(handler)

        template = self._environment.get_template('error-5xx.html')
        html = await template.render_async({
            'status_code': response.status_code,
            'status_text': response.status_text,
            'method': request.method,
            'path': request.raw_path.decode('ascii'),
            'handler_file': source_file,
            'handler_lines': source_lines[0],
            'handler_line_offset': source_lines[1],
            'handler_name': handler.__name__ + str(signature(handler)),
            'exception_name': str(exc_info()[0]),
            'exception_format': format_exc()
        })

        await response.send_html(html)
