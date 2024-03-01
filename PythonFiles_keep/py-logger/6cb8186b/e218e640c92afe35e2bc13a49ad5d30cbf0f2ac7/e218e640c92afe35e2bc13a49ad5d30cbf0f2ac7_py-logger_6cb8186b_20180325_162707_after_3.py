import requests
import os
from . import logger
import sys

url = os.environ.get('SLACK_WEBHOOK_URL')

if not url:
    logger.red('You need to set env var SLACK_WEBHOOK_URL first')
    sys.exit(1)


def send(title, message):
    res = requests.post(url, json={"text": "", "attachments": [{
        "title": title,
        "text": message
    }]})
    return res


if __name__ == '__main__':
    send("this is title", 'this is msg')
