from io import BytesIO

from email.utils import formatdate
from time import time
from typing import Mapping, Optional, Union
from urllib.parse import quote

import anyio
from fastapi.responses import FileResponse
from starlette._compat import md5_hexdigest
from starlette.background import BackgroundTask
from starlette.types import Receive, Scope, Send

class BytesFileResponse(FileResponse):
    chunk_size = 64 * 1024

    def __init__(
        self,
        content: bytes,
        status_code: int=200,
        headers: Optional[Mapping[str, str]]=None,
        background: Optional[BackgroundTask] = None,
        media_type: Optional[str]=None,
        filename: Optional[str]=None,
        method: Optional[str]=None,
        content_disposition_type: str="attachment",
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.filename = filename
        self.send_header_only = method is not None and method.upper() == "HEAD"
        media_type = "application/octet-stream" if media_type is None else media_type
        self.media_type = media_type
        self.background = background
        self.init_headers(headers)
        if self.filename is not None:
            content_disposition_filename = quote(self.filename)
            if content_disposition_filename != self.filename:
                content_disposition = "{}; filename*=utf-8''{}".format(
                    content_disposition_type, content_disposition_filename
                )
            else:
                content_disposition = '{}; filename="{}"'.format(
                    content_disposition_type, self.filename
                )
            self.headers.setdefault("content-disposition", content_disposition)
        self.set_stat_headers()

    def set_stat_headers(self) -> None:
        content_length = str(len(self.content))
        last_modified = formatdate(time(), usegmt=True)
        etag_base = f"{time()}-{content_length}"
        etag = md5_hexdigest(etag_base.encode(), usedforsecurity=False)

        self.headers.setdefault("content-length", content_length)
        self.headers.setdefault("last-modified", last_modified)
        self.headers.setdefault("etag", etag)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        if self.send_header_only:
            await send({"type": "http.response.body", "body": b"", "more_body": False})
        else:
            bytes_io = BytesIO(self.content)
            more_body = True
            while more_body:
                chunk = 
                more_body = len(chunk) == self.chunk_size
                await send(
                    {
                        "type": "http.response.body",
                        "body": bytes_io.getbuffer(),
                        "more_body": more_body,
                    }
                )
        if self.background is not None:
            await self.background()
