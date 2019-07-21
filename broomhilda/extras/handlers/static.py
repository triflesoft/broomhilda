class StaticHandler: # pylint: disable=R0903
    def __init__(self, base_path, index=True, single_chunk_limit=64*1024):
        from os.path import abspath

        self._base_path = abspath(base_path)
        self._index = index
        self._single_chunk_limit = single_chunk_limit

    async def get(self, request, response, path): # pylint: disable=R0914,W0613
        from datetime import datetime
        from mimetypes import guess_type
        from os import scandir
        from os import stat
        from os.path import abspath
        from os.path import isdir
        from os.path import isfile
        from os.path import join
        from broomhilda.facade.shared.headers import ContentTypeHeader

        final_path = abspath(join(self._base_path, path))

        if isfile(final_path):
            stat_result = stat(final_path)
            mime_type = guess_type(final_path)[0]

            if mime_type:
                response.headers.content_type = ContentTypeHeader(mime_type)

            response.headers.last_modified = datetime.fromtimestamp(stat_result.st_mtime)

            if stat_result.st_size < self._single_chunk_limit:
                response.headers.content_length = stat_result.st_size

                with open(final_path, 'rb') as file:
                    data = file.read()
                    await response.send_body(data)
            else:
                with open(final_path, 'rb') as file:
                    async with response.open_body() as stream:
                        while True:
                            data = file.read(self._single_chunk_limit)

                            if not data:
                                break

                            await stream.write(data)
        elif isdir(final_path) and self._index:
            result = f'''
<html>
    <head>
        <title>{path}</title>
        <style>
html {{ font-family: monospace }}
table {{ width: 100%; }}
tr:nth-child(odd) {{ background-color: #EEE; }}
tr > *:nth-child(1) {{ text-align: left; }}
tr > *:nth-child(2) {{ text-align: right; }}
tr > *:nth-child(3) {{ text-align: right; }}
        </style>
    </head>
    <body>
        <h1>Location: {path}</h1>
        <table>
            <tr><th>Name</th><th>Last modified</th><th>Size</th></tr>
'''

            for entry in scandir(final_path):
                stat_result = entry.stat()
                mtime = datetime.fromtimestamp(stat_result.st_mtime)

                if entry.is_dir():
                    result += f'<tr><td><a href="{join(path, entry.name)}/">{entry.name}/</a></td><td>{mtime:%Y-%m-%d %H:%M:%S}</td><td>-</td></tr>'
                else:
                    result += f'<tr><td><a href="{join(path, entry.name)}">{entry.name}</a></td><td>{mtime:%Y-%m-%d %H:%M:%S}</td><td>{stat_result.st_size:,d}</td></tr>'

            result += '''
        </table>
    </body>
</html>'''
            await response.send_html(result)
        else:
            response.status_code = 404
