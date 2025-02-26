from smsclient import SMSClient
from config import Config
import argparse
import asyncio
import logging

async def main():
    Config("config.toml")
    parser = argparse.ArgumentParser(description="SMS API client")
    parser.add_argument('-s', '--sender', type=str, help="Sender's phone number", required=True)
    parser.add_argument('-r', '--recipient', type=str, help="Recipient's phone number", required=True)
    parser.add_argument('-m', '--message', type=str, help="Message's body", required=True)
    parser.add_argument('-d', '--debug', help="Print debug messages", action='store_true')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')
    async with SMSClient(Config) as client:
        response, json = await client.request(args.sender, args.recipient, args.message)
        print(f"[{response.status_code} {response.reason_phrase}]")
        print(json)

if __name__ == '__main__':
    asyncio.run(main())