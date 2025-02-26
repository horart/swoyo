from typing import Optional, Self
import base64

class HTTPRequest:
    """Class representing an HTTP request"""

    host: str
    payload: str
    http_version: str
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    method: str
    path: str
    content_type: str
    
    
    def __init__(self, host: str, method: str, path: str, payload: str, *, authorization: dict = None, http_version: str = '1.1', content_type: str = "application/json"):
        self.host = host
        self.method = method
        self.payload = payload
        self.http_version = http_version
        self.path = path
        self.content_type = content_type
        if authorization is not None:
            self.auth_username = authorization['username']
            self.auth_password = authorization['password']

    def get_content_length(self) -> int:
        """Get size of content in bytes"""
        return len(self.payload.encode())

    def to_bytes(self) -> bytes:
        """Convert to bytes according to the HTTP format"""
        authorization = f'\r\nAuthorization: Basic {base64.encodebytes(f'{self.auth_username}:{self.auth_password}'.encode())[:-1].decode()}' if self.auth_username is not None else ''

        return f"""{self.method} {self.path} HTTP/{self.http_version}\r
Host: {self.host}{authorization}\r
Content-Type: {self.content_type}\r
Content-Length: {self.get_content_length()}\r
\r
{self.payload}""".encode("utf-8")
    
    @staticmethod
    def from_bytes(binary_data: bytes) -> Self:
        """Create HTTPRequest from binary request"""
        s = binary_data.decode().split('\r\n')
        method, path, http_version = s[0].split()
        http_version = http_version.split('/')[1]
        hostname = None
        auth_login = None
        auth_password = None
        for idx, header in enumerate(s[1:], start=1):
            if header.startswith('Host: '):
                hostname = ' '.join(header.split(' ')[1:])
            if header.startswith('Authorization: '):
                auth_login, auth_password = base64.decodebytes(header.split(' ')[2].encode()).decode().split(':')
            if header == '':
                break

        payload = '\r\n'.join(s[idx+1:])

        authorization = auth_login and {'username': auth_login, 'password': auth_password}
        return HTTPRequest(hostname, method, path, payload, authorization=authorization, http_version=http_version)


class HTTPRequestFactory:
    """Factory class for building requests for the same webservice"""

    host: str
    http_version: str
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    content_type: str

    def __init__(self, host: str, *, authorization: dict = None, http_version = '1.1', content_type='application/json'):
        self.host = host
        self.http_version = http_version
        self.content_type = content_type
        if authorization is not None:
            self.auth_username = authorization['username']
            self.auth_password = authorization['password']

    def build(self, method: str, path: str, payload: str, *, content_type: str = None) -> HTTPRequest:
        """Build a request"""
        authorization = {'username': self.auth_username, 'password': self.auth_password} if self.auth_username else None
        return HTTPRequest(self.host, method, path, payload, authorization=authorization,
                           http_version=self.http_version,
                           content_type=(self.content_type if content_type is None else content_type))