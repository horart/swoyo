from smsclient import SMSClient
from config import Config
import argparse
import asyncio

async def main():
    Config("config.toml")
    parser = argparse.ArgumentParser(description="SMS API client")
    parser.add_argument('-s', '--sender', type=str, help="Sender's phone number", required=True)
    parser.add_argument('-r', '--recipient', type=str, help="Recipient's phone number", required=True)
    parser.add_argument('-m', '--message', type=str, help="Message's body", required=True)
    parser.add_argument('-d', '--debug', type=bool, help="Print debug messages")
    args = parser.parse_args()
    async with SMSClient(Config) as client:
        await client.connect()
        await client.request(args.sender, args.recipient, args.message)

if __name__ == '__main__':
    asyncio.run(main())