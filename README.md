# Asynchronous CLI client for SMS service
Setup:
```
pip install -r requirements.txt
```

Dependencies:
* toml

Usage:
```
usage: main.py [-h] -s SENDER -r RECIPIENT -m MESSAGE [-d]

SMS API client

options:
  -h, --help            show this help message and exit
  -s SENDER, --sender SENDER
                        Sender's phone number
  -r RECIPIENT, --recipient RECIPIENT
                        Recipient's phone number
  -m MESSAGE, --message MESSAGE
                        Message's body
  -d, --debug           Print debug messages
```

Tests:
```
pip install pytest pytest-asyncio
pytest
```