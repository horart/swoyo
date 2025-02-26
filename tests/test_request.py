from swoyo.request import HTTPRequest
from swoyo.request import HTTPRequestFactory
import base64
import pytest

class TestRequest:

    def test___init___authorization_none(self):
        """
        Test that when authorization is None, auth_username and auth_password are not set.
        """
        request = HTTPRequest("example.com", "GET", "/path", "payload", authorization=None)
        assert request.auth_username is None
        assert request.auth_password is None

    def test___init___authorization_provided(self):
        """
        Test that when authorization is provided, auth_username and auth_password are set correctly.
        """
        auth = {"username": "user", "password": "pass"}
        request = HTTPRequest("example.com", "GET", "/path", "payload", authorization=auth)
        assert request.auth_username == "user"
        assert request.auth_password == "pass"

    def test___init___with_authorization(self):
        """
        Test the __init__ method of HTTPRequest when authorization is provided.
        This test verifies that the HTTPRequest object is correctly initialized
        with authorization details when they are passed as an argument.
        """
        host = "example.com"
        method = "GET"
        path = "/api/data"
        payload = '{"key": "value"}'
        authorization = {"username": "user", "password": "pass"}
        http_version = "1.1"
        content_type = "application/json"

        request = HTTPRequest(host, method, path, payload, authorization=authorization,
                              http_version=http_version, content_type=content_type)

        assert request.host == host
        assert request.method == method
        assert request.path == path
        assert request.payload == payload
        assert request.http_version == http_version
        assert request.content_type == content_type
        assert request.auth_username == authorization['username']
        assert request.auth_password == authorization['password']

    def test___init___with_authorization_2(self):
        """
        Test the initialization of HTTPRequestFactory with authorization.

        This test verifies that when an authorization dictionary is provided,
        the HTTPRequestFactory correctly sets the auth_username and auth_password
        attributes.
        """
        host = "example.com"
        authorization = {"username": "testuser", "password": "testpass"}
        factory = HTTPRequestFactory(host, authorization=authorization)

        assert factory.host == host
        assert factory.http_version == "1.1"
        assert factory.content_type == "application/json"
        assert factory.auth_username == "testuser"
        assert factory.auth_password == "testpass"

    def test___init___without_authorization(self):
        """
        Test the __init__ method of HTTPRequest when authorization is not provided.

        This test verifies that the HTTPRequest object is correctly initialized
        without authorization details. It checks that the basic attributes are set
        and that auth_username and auth_password remain None.
        """
        host = "example.com"
        method = "GET"
        path = "/api/data"
        payload = '{"key": "value"}'
        http_version = "1.1"
        content_type = "application/json"

        request = HTTPRequest(host, method, path, payload, http_version=http_version, content_type=content_type)

        assert request.host == host
        assert request.method == method
        assert request.path == path
        assert request.payload == payload
        assert request.http_version == http_version
        assert request.content_type == content_type
        assert request.auth_username is None
        assert request.auth_password is None

    def test_build_custom_content_type(self):
        """
        Test that the build method correctly uses a custom content type when provided.
        This tests the edge case where a specific content type is passed to override the default.
        """
        factory = HTTPRequestFactory("example.com", content_type="application/json")
        custom_content_type = "text/plain"
        request = factory.build("GET", "/path", "payload", content_type=custom_content_type)
        assert request.content_type == custom_content_type

    def test_build_with_default_content_type(self):
        """
        Test the build method of HTTPRequestFactory when content_type is not provided.
        It should use the default content_type set in the factory.
        """
        factory = HTTPRequestFactory("example.com", content_type="application/json")
        request = factory.build("GET", "/api/data", "{}")

        assert isinstance(request, HTTPRequest)
        assert request.host == "example.com"
        assert request.method == "GET"
        assert request.path == "/api/data"
        assert request.payload == "{}"
        assert request.content_type == "application/json"
        assert request.http_version == "1.1"
        assert request.auth_username is None
        assert request.auth_password is None

    def test_build_without_authorization(self):
        """
        Test that the build method correctly handles the case when no authorization is set.
        This tests the edge case where the factory is created without authorization credentials.
        """
        factory = HTTPRequestFactory("example.com")
        request = factory.build("GET", "/path", "payload")
        assert request.auth_username is None
        assert request.auth_password is None

    def test_from_bytes_1(self):
        """
        Test the from_bytes method of HTTPRequest class.
        This test covers the case where the binary data includes Host and Authorization headers,
        and an empty header to signal the end of headers.
        """
        # Prepare test data
        method = "GET"
        path = "/test"
        http_version = "1.1"
        host = "example.com"
        username = "user"
        password = "pass"
        payload = "Test payload"

        # Construct binary data
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        binary_data = f"{method} {path} HTTP/{http_version}\r\n" \
                      f"Host: {host}\r\n" \
                      f"Authorization: Basic {auth}\r\n" \
                      f"\r\n" \
                      f"{payload}".encode()

        # Call the method under test
        result = HTTPRequest.from_bytes(binary_data)

        # Assert the results
        assert result.host == host
        assert result.method == method
        assert result.path == path
        assert result.payload == payload
        assert result.http_version == http_version
        assert result.auth_username == username
        assert result.auth_password == password

    def test_from_bytes_2(self):
        """
        Test the from_bytes method of HTTPRequest class when the input contains an Authorization header but no Host header.
        This test verifies that the method correctly parses the input, extracts the authorization credentials,
        and creates an HTTPRequest object with the appropriate attributes.
        """
        # Prepare test data
        method = "GET"
        path = "/test"
        http_version = "1.1"
        auth_login = "user"
        auth_password = "pass"
        payload = "Test payload"

        # Encode authorization credentials
        auth_encoded = base64.b64encode(f"{auth_login}:{auth_password}".encode()).decode()

        # Create the binary input data
        binary_data = f"{method} {path} HTTP/{http_version}\r\nAuthorization: Basic {auth_encoded}\r\n\r\n{payload}".encode()

        # Call the method under test
        result = HTTPRequest.from_bytes(binary_data)

        # Assert the expected results
        assert result.method == method
        assert result.path == path
        assert result.http_version == http_version
        assert result.auth_username == auth_login
        assert result.auth_password == auth_password
        assert result.payload == payload
        assert result.host is None  # No Host header in the input

    def test_from_bytes_3(self):
        """
        Test the from_bytes method when the input contains a Host header but no Authorization header.
        It should correctly parse the method, path, HTTP version, hostname, and payload.
        """
        binary_data = b"GET /path HTTP/1.1\r\nHost: example.com\r\n\r\nSample payload"
        request = HTTPRequest.from_bytes(binary_data)

        assert request.method == "GET"
        assert request.path == "/path"
        assert request.http_version == "1.1"
        assert request.host == "example.com"
        assert request.payload == "Sample payload"
        assert request.auth_username is None
        assert request.auth_password is None

    def test_from_bytes_4(self):
        """
        Test the from_bytes method of HTTPRequest class when the input contains
        both Host and Authorization headers, but no empty header.

        This test verifies that the method correctly parses the binary data
        and creates an HTTPRequest object with the expected attributes,
        including the authorization information.
        """
        # Prepare test data
        binary_data = b"GET /path HTTP/1.1\r\nHost: example.com\r\nAuthorization: Basic dXNlcjpwYXNz\r\nContent-Type: application/json\r\nContent-Length: 13\r\n\r\n{'key':'value'}"

        # Call the method under test
        request = HTTPRequest.from_bytes(binary_data)

        # Assert the expected results
        assert request.host == "example.com"
        assert request.method == "GET"
        assert request.path == "/path"
        assert request.http_version == "1.1"
        assert request.auth_username == "user"
        assert request.auth_password == "pass"
        assert request.payload == "{'key':'value'}"

    def test_from_bytes_invalid_input(self):
        """
        Test the from_bytes method with invalid input (empty bytes).
        This tests the edge case where the input is empty, which should raise a ValueError.
        """
        with pytest.raises(ValueError):
            HTTPRequest.from_bytes(b'')

    def test_from_bytes_malformed_request_line(self):
        """
        Test the from_bytes method with a malformed request line.
        This tests the edge case where the request line is incomplete,
        which should raise a ValueError.
        """
        malformed_request = b'GET /path\r\nHost: example.com\r\n\r\n'
        with pytest.raises(ValueError):
            HTTPRequest.from_bytes(malformed_request)

    def test_from_bytes_missing_headers(self):
        """
        Test the from_bytes method with missing required headers.
        This tests the edge case where the input is missing the Host header,
        which should result in hostname being None.
        """
        invalid_request = b'GET /path HTTP/1.1\r\n\r\n'
        result = HTTPRequest.from_bytes(invalid_request)
        assert result.host is None

    def test_get_content_length_1(self):
        """
        Test that get_content_length returns the correct length of the encoded payload.
        This test verifies that the method accurately calculates the size of the content in bytes.
        """
        request = HTTPRequest("example.com", "GET", "/", "Hello, World!")
        expected_length = len("Hello, World!".encode())
        assert request.get_content_length() == expected_length

    def test_get_content_length_empty_payload(self):
        """
        Test get_content_length method with an empty payload.
        This is an edge case where the payload is an empty string.
        """
        request = HTTPRequest("example.com", "GET", "/", "")
        assert request.get_content_length() == 0

    def test_get_content_length_non_ascii_payload(self):
        """
        Test get_content_length method with a payload containing non-ASCII characters.
        This tests the encoding behavior of the method.
        """
        request = HTTPRequest("example.com", "POST", "/", "こんにちは")  # Hello in Japanese
        assert request.get_content_length() == 15  # 5 characters, each 3 bytes in UTF-8

    def test_to_bytes_1(self):
        """
        Test the to_bytes method of HTTPRequest class.

        This test verifies that the to_bytes method correctly converts the HTTPRequest object
        to bytes according to the HTTP format, including method, path, HTTP version, host,
        content type, content length, and payload.
        """
        request = HTTPRequest("example.com", "GET", "/path", "payload")
        expected_bytes = b"GET /path HTTP/1.1\r\nHost: example.com\r\nContent-Type: application/json\r\nContent-Length: 7\r\n\r\npayload"
        assert request.to_bytes() == expected_bytes

    def test_to_bytes_with_null_auth(self):
        """
        Test to_bytes method when auth_username is None.
        This tests the edge case where authorization is not provided.
        """
        request = HTTPRequest("example.com", "GET", "/", "")
        result = request.to_bytes()
        expected = b"GET / HTTP/1.1\r\nHost: example.com\r\nContent-Type: application/json\r\nContent-Length: 0\r\n\r\n"
        assert result == expected
