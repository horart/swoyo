from typing import Tuple
import config
import asyncio
import logging
from request import HTTPRequestFactory
from response import HTTPResponse
import json

class SMSClient:
    """SMS API Client class"""
    
    server_address: str
    server_port: int
    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter
    _request_factory: HTTPRequestFactory
    connected: bool = False

    def __init__(self, config: config.Config):
        self.server_address = config.server['address']
        self.server_port = config.server['port']
        self._request_factory = HTTPRequestFactory(config.server['hostname'], authorization=config.authorization, http_version=config.http['version'])


    async def request(self, sender: str, recipient: str, message: str) -> Tuple[HTTPResponse, dict]:
        """Send "Send SMS" request to server"""
        if not self.connected:
            raise ConnectionError("Not connected: run connect()")
        
        request = self._request_factory.build('POST', '/send_sms', json.dumps({
            'sender': sender,
            'recipient': recipient,
            'message': message,
        }))
        logging.info(f"Request formed")
        self._writer.write(request.to_bytes())
        await self._writer.drain()
        logging.info("Request sent")
        received = await self._reader.readuntil(b'\r\n\r\n')
        content_length = int(received.split(b'Content-Length: ')[1].split(b'\r\n')[0])
        received += await self._reader.readexactly(content_length)
        logging.info("Response received")
        response = HTTPResponse.from_bytes(received)
        try:
            body = json.loads(response.body)
        except json.JSONDecodeError:
            body = None
        return response, body

    async def connect(self) -> None:
        """Connect to server"""
        if self.connected:
            return self
        logging.info(f"Opening connection to {self.server_address}:{self.server_port}")
        self._reader, self._writer = await asyncio.open_connection(self.server_address, self.server_port)
        logging.info(f"Connection to {self.server_address}:{self.server_port} established")
        self.connected = True

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        if not self.connected:
            return
        logging.info("Closing connection")
        self._writer.close()
        await self._writer.wait_closed()
        logging.info("Connection closed")
        self.connected = False