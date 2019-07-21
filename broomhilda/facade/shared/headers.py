from multidict import CIMultiDict


class AuthorizationHeader:
    __slots__ = 'type', 'credentials', 'username', 'password', 'token', 'value'

    @classmethod
    def _from_value(cls, value):
        if value:
            if ' ' in value:
                type, credentials = value.split(' ', 1)

                return cls(type, credentials, value)

        return None

    def __init__(self, type, credentials, value):
        from base64 import standard_b64decode
        from binascii import Error as BinAsciiError

        self.type = type
        self.credentials = credentials
        self.value = value

        if self.type == 'basic':
            try:
                userinfo = standard_b64decode(self.credentials)
                self.username, self.password = userinfo.split(':', 1)
            except BinAsciiError:
                pass
        elif self.type == 'bearer':
            self.token = self.credentials


class ContentDispositionHeader:
    __slots__ = 'type', 'params', 'value'

    def __init__(self, type, params, value):
        self.type = type
        self.params = params
        self.value = value

    def __str__(self):
        return self.value


class ContentTypeHeader:
    __slots__ = 'type', 'subtype', 'suffix', 'params', 'value'

    @classmethod
    def _from_value(cls, value):
        if value:
            if '/' in value:
                parts = value.split(';')
                type, subtype_suffix = parts[0].split('/', 1)

                if '+' in subtype_suffix:
                    subtype, suffix = subtype_suffix.split('+', 1)
                else:
                    subtype, suffix = subtype_suffix, ''

                params = {}

                for part in parts[1:]:
                    name, value = part.split('=')
                    params[name.strip().lower()] = value.strip()

                return ContentTypeHeader(type.strip().lower(), subtype.strip().lower(), suffix.strip().lower(), params, value)

        return None

    def __init__(self, type, subtype=None, suffix=None, params=None, value=None):
        if ('/' in type) and (subtype is None):
            self.type, self.subtype = type.split('/', 1)
        else:
            self.type = type
            self.subtype = subtype

        self.suffix = suffix
        self.params = params
        self.value = f'{self.type}/{self.subtype}'

        if self.suffix:
            self.value += '+' + self.suffix

        if self.params:
            self.value += ''.join([f';{name}={value}' for name, value in self.params.items()])

    def __str__(self):
        return self.value


class _UserAgentBrowser:
    __slots__ = 'family', 'major', 'minor', 'patch'

    def __init__(self, family, major, minor, patch):
        self.family = family
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        if self.major:
            if self.minor:
                if self.patch:
                    return f'{self.family}/{self.major}.{self.minor}.{self.patch}'
                else:
                    return f'{self.family}/{self.major}.{self.minor}'
            else:
                return f'{self.family}/{self.major}'
        else:
            return self.family


class _UserAgentOperatingSystem:
    __slots__ = 'family', 'major', 'minor', 'patch', 'patch_minor'

    def __init__(self, family, major, minor, patch, patch_minor):
        self.family = family
        self.major = major
        self.minor = minor
        self.patch = patch
        self.patch_minor = patch_minor

    def __str__(self):
        if self.major:
            if self.minor:
                if self.patch:
                    if self.patch:
                        return f'{self.family}/{self.major}.{self.minor}.{self.patch}.{self.patch_minor}'
                    else:
                        return f'{self.family}/{self.major}.{self.minor}.{self.patch}'
                else:
                    return f'{self.family}/{self.major}.{self.minor}'
            else:
                return f'{self.family}/{self.major}'
        else:
            return self.family


class _UserAgentDevice:
    __slots__ = 'family', 'brand', 'model'

    def __init__(self, family, brand, model):
        self.family = family
        self.brand = brand
        self.model = model

    def __str__(self):
        if self.brand:
            if self.model:
                return f'{self.family}/{self.brand}.{self.model}'
            else:
                return f'{self.family}/{self.brand}'
        else:
            return self.family


class UserAgentHeader:
    __slots__ = 'browser', 'operating_system', 'device', 'value'

    @classmethod
    def _from_value(cls, value):
        from ua_parser import user_agent_parser

        if value:
            user_agent_data = user_agent_parser.Parse(value)

            return cls(
                _UserAgentBrowser(
                    user_agent_data['user_agent'].get('family'),
                    user_agent_data['user_agent'].get('major'),
                    user_agent_data['user_agent'].get('minor'),
                    user_agent_data['user_agent'].get('patch')
                ),
                _UserAgentOperatingSystem(
                    user_agent_data['os'].get('family'),
                    user_agent_data['os'].get('major'),
                    user_agent_data['os'].get('minor'),
                    user_agent_data['os'].get('patch'),
                    user_agent_data['os'].get('patch_minor')
                ),
                _UserAgentDevice(
                    user_agent_data['os'].get('family'),
                    user_agent_data['os'].get('brand'),
                    user_agent_data['os'].get('model')
                ),
                value)

        return None

    def __init__(self, browser, operating_system, device, value):
        self.browser = browser
        self.operating_system = operating_system
        self.device = device
        self.value = value

    def __str__(self):
        return self.value


class HeadersBase(CIMultiDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_disposition = None
        self.content_length = None
        self.content_md5 = None
        self.content_type = None
        self.date = None


class FormPartHeadersBase(HeadersBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _post_process(self,):
        # Content-Disposition
        content_disposition_value = self.get('Content-Disposition')

        if content_disposition_value:
            parts = content_disposition_value.split(';')
            params = {}

            for part in parts[1:]:
                name, value = part.split('=')
                params[name.strip().lower()] = value.strip()

            self.content_disposition = ContentDispositionHeader(parts[0].strip().lower(), params, content_disposition_value)

        # Content-Type
        self.content_type = ContentTypeHeader._from_value(self.get('Content-Type'))


class RequestHeadersBase(HeadersBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authorization = None
        self.user_agent = None


class ResponseHeadersBase(HeadersBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_length = None
        self.content_type = None
        self.last_modified = None
