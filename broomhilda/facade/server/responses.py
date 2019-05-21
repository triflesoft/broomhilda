from json import dumps

from broomhilda.facade.server.headers import ServerResponseHeaders


STATUS_DATA = {
    100: b'Continue',
    101: b'Switching Protocols',
    102: b'Processing',
    103: b'Early Hints',
    200: b'OK',
    201: b'Created',
    202: b'Accepted',
    203: b'Non-Authoritative Information',
    204: b'No Content',
    205: b'Reset Content',
    206: b'Partial Content',
    207: b'Multi-Status',
    208: b'Already Reported (WebDAV; RFC 5842)',
    226: b'IM Used',
    300: b'Multiple Choices',
    301: b'Moved Permanently',
    302: b'Found',
    303: b'See Other',
    304: b'Not Modified',
    305: b'Use Proxy',
    306: b'Switch Proxy',
    307: b'Temporary Redirect',
    308: b'Permanent Redirect',
    400: b'Bad Request',
    401: b'Unauthorized',
    402: b'Payment Required',
    403: b'Forbidden',
    404: b'Not Found',
    405: b'Method Not Allowed',
    406: b'Not Acceptable',
    407: b'Proxy Authentication Required',
    408: b'Request Timeout',
    409: b'Conflict',
    410: b'Gone',
    411: b'Length Required',
    412: b'Precondition Failed',
    413: b'Payload Too Large',
    414: b'URI Too Long',
    415: b'Unsupported Media Type',
    416: b'Range Not Satisfiable',
    417: b'Expectation Failed',
    418: b'I\'m a teapot',
    421: b'Misdirected Request',
    422: b'Unprocessable Entity',
    423: b'Locked',
    424: b'Failed Dependency',
    426: b'Upgrade Required',
    428: b'Precondition Required',
    429: b'Too Many Requests',
    431: b'Request Header Fields Too Large',
    451: b'Unavailable For Legal Reasons',
    500: b'Internal Server Error',
    501: b'Not Implemented',
    502: b'Bad Gateway',
    503: b'Service Unavailable',
    504: b'Gateway Timeout',
    505: b'HTTP Version Not Supported',
    506: b'Variant Also Negotiates',
    507: b'Insufficient Storage',
    508: b'Loop Detected',
    510: b'Not Extended',
    511: b'Network Authentication Required',
}


STATUS_TEXT = { code: data.decode('ascii') for code, data in STATUS_DATA.items() }


class ServerResponseBodyStream(object):
    def __init__(self, response):
        self.response = response

    async def write(self, data):
        await self.response._send_headers()
        await self.response._connection.write_response(b'%x\r\n' % len(data))
        await self.response._connection.write_response(data)
        await self.response._connection.write_response(b'\r\n')

    async def close(self):
        await self.response._connection.write_response(b'0\r\n\r\n')


class ServerResponseBodyStreamContext(object):
    def __init__(self, response):
        self.response = response
        self.stream = ServerResponseBodyStream(self.response)

    async def __aenter__(self):
        return self.stream

    async def __aexit__(self, exc_type, exc, tb):
        await self.stream.close()


class ServerResponse(object):
    async def _send_headers(self):
        if not self._are_headers_sent:
            self._are_headers_sent = True

            self.headers._post_process(self)

            lines = [
                b'HTTP/%s %03d %s\r\n' % (self._version.encode('ascii'), self.status_code, self.status_text.encode('ascii'))
            ]

            for name, value in self.headers.items():
                name = name.encode('ascii')

                if type(value) is str:
                    value = value.encode('ascii')

                lines.append(b'%b: %b\r\n' % (name, value))

            lines.append(b'\r\n')

            await self._connection.write_response(b''.join(lines))

    async def _send_body(self, data):
        if not self._is_body_sent:
            self._is_body_sent = True
            await self._connection.write_response(data)

    def _get_status_code(self):
        return self._status_code

    def _set_status_code(self, value):
        if self._status_code != value:
            self._status_code = value
            self._status_text = None

    def _get_status_text(self):
        if not self._status_text:
            self._status_text = self._status_text if self._status_text else STATUS_TEXT.get(self._status_code, 'Undefined')

        return self._status_text

    def _set_status_text(self, value):
        self._status_text = value

    def __init__(self, connection, version, status_code=200, status_text=None, headers=None):
        self._connection = connection
        self._version = version
        self._are_headers_sent = False
        self._is_body_sent = False
        self._status_code = status_code
        self._status_text = status_text
        self.headers = ServerResponseHeaders()

        if headers:
            for name, value in headers:
                self.headers[name] = value

    status_code = property(_get_status_code, _set_status_code)
    status_text = property(_get_status_text, _set_status_text)

    async def send_body(self, data):
        self.headers['Content-Length'] = str(len(data))

        await self._send_headers()
        await self._send_body(data)

    async def send_text(self, text):
        if not 'Content-Type' in self.headers:
            self.headers['Content-Type'] = 'text/plain; charset=utf-8'

        await self.send_body(text.encode('utf-8'))

    async def send_html(self, text):
        if not 'Content-Type' in self.headers:
            self.headers['Content-Type'] = 'text/html; charset=utf-8'

        await self.send_body(text.encode('utf-8'))

    async def send_json(self, json, *args, **kwargs):
        if not 'Content-Type' in self.headers:
            self.headers['Content-Type'] = 'application/json; charset=utf-8'

        await self.send_text(dumps(json, *args, **kwargs))

    def open_body(self):
        try:
            del self.headers['Content-Length']
        except KeyError:
            pass

        self.headers['Transfer-Encoding'] = b'chunked'
        self._is_body_sent = True

        return ServerResponseBodyStreamContext(self)
