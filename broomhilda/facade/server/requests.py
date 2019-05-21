from email.message import Message
from email.parser import BytesFeedParser
from email.policy import HTTP
from httptools import HttpRequestParser
from httptools import parse_url
from json import loads
from multidict import CIMultiDict
from urllib.parse import parse_qs
from urllib.parse import unquote_to_bytes

from broomhilda.facade.server.headers import ServerFormPartHeaders
from broomhilda.facade.server.headers import ServerRequestHeaders


class ServerRequestBodyStream(object):
    def __init__(self, request):
        self.request = request

    async def read(self, max_length=64*1024):
        return await self.request._read_body(max_length)

    async def readall(self):
        body = b''

        while True:
            data = await self.request._read_body(64 * 1024)

            if not data:
                break

            body += data

        return body


class ServerRequestBodyStreamContext(object):
    def __init__(self, request):
        self.request = request
        self.stream = ServerRequestBodyStream(self.request)

    async def __aenter__(self):
        return self.stream

    async def __aexit__(self, exc_type, exc, tb):
        pass


def message_factory():
    message = Message(policy=HTTP)
    message.set_default_type('application/form-data')

    return message


class ServerRequestFilePart(object):
    def __init__(self, filename, headers, content):
        self.filename = filename
        self.headers = ServerFormPartHeaders()
        self.content = content

        for name, value in headers:
            self.headers.add(name, value)

    def __str__(self):
        return self.filename


class ServerRequest(object):
    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        self.raw_path += url

    def on_header(self, name: bytes, value: bytes):
        str_name = name.decode('ascii')
        str_value = value.decode('ascii')

        self.raw_headers.add(str_name, value)
        self.headers.add(str_name, str_value)

    def on_headers_complete(self):
        parsed_path = parse_url(self.raw_path)

        self.version = self._parser.get_http_version()
        self.keep_alive = self._parser.should_keep_alive()
        self.upgrade = self._parser.should_upgrade()
        self.raw_method = self._parser.get_method()
        self.method = self.raw_method.decode('ascii')
        self.path = parsed_path.path.decode('ascii')

        for name, values in parse_qs(parsed_path.query,).items():
            for value in values:
                self.raw_query.add(name.decode('ascii'), value)
                self.query.add(name.decode('ascii'), value.decode('ascii'))

        self.headers._post_process(self)
        self._headers_complete = True

        if self.headers.content_length:
            self._body_length = self.headers.content_length

    def on_body(self, body: bytes):
        self._body_buffer += body

    def on_message_complete(self):
        self._is_body_complete = True

    def on_chunk_header(self):
        pass

    def on_chunk_complete(self):
        pass

    async def _try_read_headers(self):
        while not self._headers_complete:
            data = await self._connection.read_request(64 * 1024)

            if not data:
                return False

            self._parser.feed_data(data)

        return True

    async def _read_body(self, max_length=64*1024):
        while (not self._is_body_complete) or (len(self._body_buffer) > 0):
            chunk_length = min(max_length, self._body_length - (self._body_position + len(self._body_buffer))) 
            data = await self._connection.read_request(chunk_length)

            if not data:
                self._is_body_complete = True
            else:
                self._body_position += len(data)
                self._parser.feed_data(data)

            if self._body_position == self._body_length:
                self._is_body_complete = True

            if len(self._body_buffer) > 0:
                result = self._body_buffer
                self._body_buffer = b''

                return result

        return b''

    def __init__(self, connection):
        self._connection = connection
        self._parser = HttpRequestParser(self)
        self._body_buffer = b''
        self._headers_complete = False
        self._is_body_complete = False

        self.version = None
        self.keep_alive = None
        self.upgrade = None
        self.address = connection.address
        self.raw_method = b''
        self.raw_headers = CIMultiDict()
        self.raw_query = CIMultiDict()
        self.raw_path = b''

        self.method = ''
        self.host = 'localhost'
        self.port = 80
        self.headers = ServerRequestHeaders()
        self.query = CIMultiDict()
        self.cookies = {}
        self.path = ''
        self.content_type_main = 'application'
        self.content_type_sub = 'octet-stream'
        self.content_type_params = {}
        self.content_charset = 'ascii'

        self._body_length = 2**32
        self._body_position = 0
        self._is_body_complete = False
        self._body = None
        self._text = None
        self._json = None
        self._form = None

    async def read_body(self):
        if self._body is None:
            async with self.open_body() as stream:
                self._body = await stream.readall()

        return self._body

    async def read_text(self):
        if self._text is None:
            charset = self.content_type_params.get('charset', 'ascii')

            self._text = self.read_body().decode(charset)

        return self._text

    async def read_json(self):
        if self._json is None:
            self._json = loads(self.read_text())

        return self._json

    async def read_form(self):
        if self._form is None:
            self._form = CIMultiDict()

            if (self.headers.content_type.type == 'application') and (self.headers.content_type.subtype == 'x-www-form-urlencoded'):
                body = await self.read_body()

                for parameter in body.split(b'&'):
                    name, value = parameter.split(b'=')
                    self._form.add(
                        unquote_to_bytes(name).decode('utf-8'),
                        unquote_to_bytes(value).decode('utf-8'))
            elif (self.headers.content_type.type == 'multipart') and (self.headers.content_type.subtype == 'form-data'):
                # TODO: replace with multifruits
                parser = BytesFeedParser(policy=HTTP, _factory=message_factory)
                parser.feed(b'Content-Type: %s\r\n\r\n' % self.raw_headers['Content-Type'])

                async with self.open_body() as stream:
                    while True:
                        data = await stream.read()

                        if not data:
                            break

                        parser.feed(data)

                message = parser.close()

                for part in message.walk():
                    if part.get_content_type() != 'multipart/form-data':
                        params = dict(part.get_params(header='content-disposition'))
                        name = params.get('name')

                        if name:
                            payload =  part.get_payload(decode=True)

                            if payload:
                                if part.get_content_type() == 'application/form-data':
                                    self._form.add(name, payload.decode('utf-8'))
                                else:
                                    self._form.add(
                                        name,
                                        ServerRequestFilePart(params.get('filename'), part.items(), part.get_payload(decode=True)))

        return self._form

    def open_body(self):
        return ServerRequestBodyStreamContext(self)
