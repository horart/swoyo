from typing import Optional, Self

class HTTPRequest:
    """Class representing an HTTP request"""

    host: str
    payload: str
    http_version: str
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    method: str
    path: str
    
    
    def __init__(self, host: str, method: str, path: str, payload: str, *, authorization: dict = None, http_version = "1.1"):
        self.host = host
        self.method = method
        self.payload = payload
        self.http_version = http_version
        self.path = path
        if authorization is not None:
            self.auth_username = authorization['username']
            self.auth_password = authorization['password']

    def get_content_length(self) -> int:
        """Get size of content in bytes"""
        return len(self.payload.encode())

    def to_bytes(self) -> bytes:
        """Convert to bytes according to the HTTP format"""
        authorization = f'\r\nAuthorization: Basic {self.auth_username}:{self.auth_password}' if self.auth_username is not None else ''

        return f"""{self.method} {self.path} HTTP/{self.http_version}\r
Host: {self.host}{authorization}\r
\r
{self.payload}\r
""".encode("utf-8")
    
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
                auth_login, auth_password = header.split(' ')[2].split(':')
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

    def __init__(self, host: str, *, authorization: dict = None, http_version = "1.1"):
        self.host = host
        self.http_version = http_version
        if authorization is not None:
            self.auth_username = authorization['username']
            self.auth_password = authorization['password']

    def build(self, method: str, path: str, payload: str) -> HTTPRequest:
        """Build a request"""
        return HTTPRequest(self.host, method, path, payload, authorization=self.auth_password, http_version=self.http_version)