from base64 import standard_b64decode
from email.utils import format_datetime
from email.utils import parsedate_to_datetime

from broomhilda.facade.shared.headers import AuthorizationHeader
from broomhilda.facade.shared.headers import ContentTypeHeader
from broomhilda.facade.shared.headers import FormPartHeadersBase
from broomhilda.facade.shared.headers import RequestHeadersBase
from broomhilda.facade.shared.headers import ResponseHeadersBase
from broomhilda.facade.shared.headers import UserAgentHeader


class ServerFormPartHeaders(FormPartHeadersBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ServerRequestHeaders(RequestHeadersBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _post_process(self, request):
        # TODO: A-IM
        # TODO: Accept
        # TODO: Accept-Charset
        # TODO: Accept-Datetime
        # TODO: Accept-Encoding
        # TODO: Accept-Language
        # TODO: Access-Control-Request-Headers
        # TODO: Access-Control-Request-Method
        # Authorization
        self.authorization = AuthorizationHeader._from_value(self.get('Authorization'))

        # TODO: Cache-Control
        # TODO: Connection
        # Content-Length
        content_length_value = self.get('Content-Length')

        if content_length_value:
            try:
                self.content_length = int(content_length_value)
            except ValueError:
                pass

        # Content-MD5
        content_md5_value = self.get('Content-MD5')

        if content_md5_value:
            try:
                self.content_md5 = standard_b64decode(content_md5_value)
            except:
                pass

        # Content-Type
        self.content_type = ContentTypeHeader._from_value(self.get('Content-Type'))

        # Cookie
        cookie_value = self.get('Cookie')

        if cookie_value:
            parts = cookie_value.split(';')

            for part in parts:
                if '=' in part:
                    name, value = part.split('=', 1)
                    request.cookies[name.strip()] = value.strip()

        # Date
        date_value = self.get('Date')

        if date_value:
            self.date = parsedate_to_datetime(date_value)

        # TODO: Expect
        # TODO: Forwarded
        # TODO: From
        # Host
        host_value = self.get('Host')

        if host_value:
            self.host = host_value

            if ':' in host_value:
                host, port = host_value.split(':', 1)

                try:
                    request.port = int(port)
                    request.host = host
                except ValueError:
                    request.host = host_value
            else:
                request.host = host_value

        # TODO: HTTP2-Settings
        # TODO: If-Match
        # TODO: If-Modified-Since
        # TODO: If-None-Match
        # TODO: If-Range
        # TODO: If-Unmodified-Since
        # TODO: Max-Forwards
        # TODO: Origin
        # TODO: Pragma
        # TODO: Proxy-Authorization
        # TODO: Range
        # TODO: Referer
        # TODO: TE
        # TODO: Upgrade
        # User-Agent
        self.user_agent = UserAgentHeader._from_value(self.get('User-Agent'))
        # TODO: Via
        # TODO: Warning


class ServerResponseHeaders(ResponseHeadersBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _post_process(self, response):
        # TODO: Accept-Patch
        # TODO: Accept-Ranges
        # TODO: Access-Control-Allow-Credentials
        # TODO: Access-Control-Allow-Headers
        # TODO: Access-Control-Allow-Methods
        # TODO: Access-Control-Allow-Origin
        # TODO: Access-Control-Expose-Headers
        # TODO: Access-Control-Max-Age
        # TODO: Age
        # TODO: Allow
        # TODO: Alt-Svc
        # TODO: Cache-Control
        # TODO: Connection
        # TODO: Content-Disposition
        # TODO: Content-Encoding
        # TODO: Content-Language
        # Content-Length
        if self.content_length:
            self['Content-Length'] = str(self.content_length)

        # TODO: Content-Location
        # TODO: Content-MD5
        # TODO: Content-Range
        # TODO: Content-Type
        if self.content_type:
            self['Content-Type'] = str(self.content_type)

        # TODO: Date
        # TODO: Delta-Base
        # TODO: ETag
        # TODO: Expires
        # TODO: IM
        # Last-Modified
        if self.last_modified:
            self['Last-Modified'] = format_datetime(self.last_modified)

        # TODO: Link
        # TODO: Location
        # TODO: P3P
        # TODO: Pragma
        # TODO: Proxy-Authenticate
        # TODO: Public-Key-Pins
        # TODO: Retry-After
        # TODO: Server
        # TODO: Set-Cookie
        # TODO: Strict-Transport-Security
        # TODO: Tk
        # TODO: Trailer
        # TODO: Transfer-Encoding
        # TODO: Upgrade
        # TODO: Vary
        # TODO: Via
        # TODO: WWW-Authenticate
        # TODO: Warning
        # TODO: X-Frame-Options
