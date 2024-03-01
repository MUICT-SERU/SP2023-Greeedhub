import os
import sys
from . import logger
import requests

KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_FROM = os.environ.get('EMAIL_FROM')
EMAIL_TO = os.environ.get('EMAIL_TO')

if not (KEY and EMAIL_FROM and EMAIL_TO):
    logger.red('check env var set properly')
    logger.red('SENDGRID_API_KEY, EMAIL_FROM, EMAIL_TO is needed')
    sys.exit(1)

receivers = [{"email": email} for email in EMAIL_TO.split(',')]


def send(title, message):
    res = requests.post('https://api.sendgrid.com/v3/mail/send', headers={
        "Authorization": "Bearer " + KEY
    }, json={
        "personalizations": [
            {
                "to": receivers,
                "subject": title
            }
        ],
        "from": {
            "email": EMAIL_FROM
        },
        "content": [
            {
                "type": "text/plain",
                "value": message
            }
        ]
    })
    return res


if __name__ == '__main__':
    send('this is title', 'this is msg')
