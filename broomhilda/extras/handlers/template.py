from jinja2 import contextfilter


__all__ = ['jinja2_template', 'Jinja2HandlerBase']


def jinja2_template(template_name):
    def jinja2_template_inner(function):
        function._template_name = template_name  # pylint: disable=W0212

        return function

    return jinja2_template_inner


def get_builtin_jinja2_loader():
    from jinja2 import FileSystemLoader
    from os.path import dirname
    from os.path import join
    from os.path import abspath

    return FileSystemLoader(abspath(join(dirname(__file__), './../../styles/')))


@contextfilter
def render_macro(context, obj, module_name, macro_name, *args):
    module = context.vars.get(module_name)

    if not module:
        return f'"{module}" cannot be found ({context.vars.keys()}).'

    macro = getattr(module, macro_name)

    if not module:
        return f'"{module}.{macro_name}" cannot be found.'

    return macro(obj, *args)


class Jinja2HandlerBase:  # pylint: disable=R0903
    def _get_wrapper(self, original_function):
        async def wrapper(request, response, *args, **kwargs):
            template = self._environment.get_template(original_function._template_name)  # pylint: disable=W0212
            result = await original_function(request, response, *args, **kwargs)
            html = await template.render_async(result)

            await response.send_html(html)

        return wrapper

    def __init__(self, environment):
        self._environment = environment
        self._environment.filters['render_macro'] = render_macro

        for method_name in ('connect', 'delete', 'get', 'head', 'options', 'patch', 'post', 'put', 'trace'):
            method = getattr(self, method_name, None)

            if callable(method) and hasattr(method, '_template_name'):
                setattr(self, method_name, self._get_wrapper(method))
