import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import asyncio
import pytest_asyncio
from smsclient import SMSClient, config, HTTPResponse  # Update import path

@pytest.fixture
def mock_config():
    cfg = MagicMock(spec=config.Config)
    cfg.server = {
        'address': 'localhost',
        'port': 4010,
        'hostname': 'localhost'
    }
    cfg.authorization = {'username': 'user', 'password': 'XXXX'}
    cfg.http = {'version': '1.1'}
    return cfg

@pytest.fixture
async def mock_client(mock_config):
    """Async fixture providing connected client and mocks"""
    client = SMSClient(mock_config)
    
    # Create async mocks with proper spec
    mock_reader = AsyncMock(spec=asyncio.StreamReader)
    mock_writer = MagicMock(spec=asyncio.StreamWriter)
    
    # Patch network connection
    with patch('asyncio.open_connection',
              new=AsyncMock(return_value=(mock_reader, mock_writer))):
        await client.connect()
    
    return (client, mock_reader, mock_writer)

@pytest.mark.asyncio
async def test_successful_request(mock_client):
    """Test successful SMS delivery"""
    client, mock_reader, mock_writer = await mock_client
    
    # Mock valid server response
    test_response = (
        b'HTTP/1.1 200 OK\r\n'
        b'Content-Type: application/json\r\n'
        b'Content-Length: 31\r\n\r\n'
        b'{"status":"success","message_id":"123"}'
    )
    
    # Configure mock reader
    mock_reader.readuntil.side_effect = [
        # Return headers
        test_response.split(b'\r\n\r\n')[0] + b'\r\n\r\n',
        # Raise error to exit readuntil loop
        asyncio.IncompleteReadError(b'', b'')
    ]
    mock_reader.readexactly = AsyncMock(
        return_value=test_response.split(b'\r\n\r\n')[1]
    )
    
    await client.connect()
    # Execute request
    response, body = await client.request(
        sender="+79123456789",
        recipient="+79098765432",
        message="Hello"
    )
    
    # Verify results
    assert response.status_code == 200
    assert body == {"status": "success", "message_id": "123"}
    mock_writer.write.assert_called_once()
    mock_writer.drain.assert_awaited_once()

@pytest.mark.asyncio
async def test_bad_request(mock_client):
    """Test invalid request handling"""
    client, mock_reader, mock_writer = await mock_client
    
    test_response = (
        b'HTTP/1.1 400 Bad Request\r\n'
        b'Content-Type: application/json\r\n'
        b'Content-Length: 32\r\n\r\n'
        b'{"error":"Invalid parameters"}'
    )
    
    mock_reader.readuntil.side_effect = [
        test_response.split(b'\r\n\r\n')[0] + b'\r\n\r\n',
        asyncio.IncompleteReadError(b'', b'')
    ]
    mock_reader.readexactly = AsyncMock(
        return_value=test_response.split(b'\r\n\r\n')[1]
    )
    await client.connect()
    response, body = await client.request(
        sender="invalid",
        recipient="invalid",
        message="Hello"
    )
    
    assert response.status_code == 400
    assert body == {"error": "Invalid parameters"}

@pytest.mark.asyncio
async def test_connection_handling(mock_config):
    """Test connection lifecycle"""
    async with SMSClient(mock_config) as client:
        await client.connect()
        assert client.connected is True
        
    # Verify clean disconnect
    assert client.connected is False

@pytest.mark.asyncio
async def test_not_connected_error(mock_config):
    """Test error when using unconnected client"""
    client = SMSClient(mock_config)
    
    with pytest.raises(ConnectionError):
        await client.request(
            sender="+79123456789",
            recipient="+79098765432",
            message="Hello"
        )

def test_request_generation(mock_config):
    """Verify HTTP request construction"""
    client = SMSClient(mock_config)
    request = client._request_factory.build(
        'POST',
        '/send_sms',
        json.dumps({
            'sender': '+79123456789',
            'recipient': '+79098765432',
            'message': 'test'
        })
    )
    
    request_bytes = request.to_bytes()
    assert b'POST /send_sms HTTP/1.1' in request_bytes
    assert b'Content-Type: application/json' in request_bytes
    assert b'Authorization: Basic ' in request_bytes
    assert b'Content-Length: ' in request_bytes