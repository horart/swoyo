from typing import Optional, Self


class HTTPResponse:
    
    status_code: int
    reason_phrase: str
    body: str
    http_version: str
    content_type: Optional[str]

    def __init__(self, body: str, status_code: int = 200, *, reason_phrase = 'OK', http_version="1.1", content_type: Optional[str] = None):
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.body = body
        self.http_version = http_version
        self.content_type = content_type


    def get_content_length(self) -> int:
        """Get size of content in bytes"""
        return len(self.body.encode())

    def to_bytes(self) -> bytes:
        """Convert to bytes according to the HTTP format"""
        content_length = self.get_content_length()
        content_type_line = f'\r\nContent-Type: {self.content_type}' if self.content_type is not None else ''
        return f"""HTTP/{self.http_version} {self.status_code} {self.reason_phrase}\r
Content-Length: {content_length}{content_type_line}\r
\r
{self.body}
""".encode()
    
    @staticmethod
    def from_bytes(binary_data: bytes) -> Self:
        """Create HTTPResponse from binary response"""
        s = binary_data.decode().split('\r\n')
        _ = s[0].split(' ')
        http_version = _[0].split('/')[1]
        status_code = int(_[1])
        reason_phrase = ' '.join(_[2:])
        content_type = None

        for idx, header in enumerate(s[1:], start=1):
            if header.startswith('Content-Type: '):
                content_type = header.split(' ')[1]
            if header == '':
                break

        body = '\r\n'.join(s[idx+1:])
        return HTTPResponse(body, status_code, reason_phrase=reason_phrase, http_version=http_version, content_type=content_type)