from swoyo.response import HTTPResponse
from typing import Optional
import pytest

class TestResponse:

    def test___init___default_parameters(self):
        """
        Test the __init__ method of HTTPResponse with default parameters.
        Verifies that the object is correctly initialized with default values when only the body is provided.
        """
        body = "Test body"
        response = HTTPResponse(body)

        assert response.body == body
        assert response.status_code == 200
        assert response.reason_phrase == 'OK'
        assert response.http_version == '1.1'
        assert response.content_type is None

    def test_get_content_length_1(self):
        """
        Test that get_content_length returns the correct length of the encoded body.
        """
        response = HTTPResponse(body="Hello, World!")
        assert response.get_content_length() == 13

    def test_get_content_length_empty_body(self):
        """
        Test get_content_length method with an empty body.
        This is an edge case where the body is an empty string, which is explicitly handled by the method.
        """
        response = HTTPResponse("")
        assert response.get_content_length() == 0

    def test_get_content_length_unicode_characters(self):
        """
        Test get_content_length method with Unicode characters in the body.
        This tests the edge case of non-ASCII characters, which are handled by the encode() method.
        """
        response = HTTPResponse("こんにちは")  # Japanese for "Hello"
        assert response.get_content_length() == 15  # Each character is 3 bytes in UTF-8

    def test_to_bytes_1(self):
        """
        Test that to_bytes() method correctly converts HTTPResponse to bytes
        with proper HTTP format, including status line, headers, and body.
        """
        response = HTTPResponse(body="Hello, World!", status_code=200, reason_phrase="OK", http_version="1.1", content_type="text/plain")
        expected_bytes = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\nContent-Type: text/plain\r\n\r\nHello, World!\n"
        assert response.to_bytes() == expected_bytes
        assert response.to_bytes() == expected_bytes
    def test_to_bytes_with_empty_body(self):
        """
        Verifies that the method correctly handles an empty body by setting Content-Length to 0.
        """
        response = HTTPResponse("")
        result = response.to_bytes()
        expected = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n\n"
        assert result == expected
        assert result == expected
        assert result == expected
        """
        Test to_bytes method when content_type is None.
        Verifies that the method handles None content_type correctly by not including a Content-Type header.
        """
        response = HTTPResponse("Test body", content_type=None)
        result = response.to_bytes()
        expected = b"HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\nTest body\n"
        assert result == expected
