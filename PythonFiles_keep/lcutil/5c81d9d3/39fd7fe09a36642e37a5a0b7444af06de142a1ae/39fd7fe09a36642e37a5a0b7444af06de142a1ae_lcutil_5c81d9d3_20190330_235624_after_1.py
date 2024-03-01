#!/usr/bin/env python

""" CLI utility to send emails.

    Example netrc.json:
    {
        "smtp" : {
            "host": "mail.example.com",
            "port": 587,
            "username": "alice@example.com",
            "password": "password",
            "from": "alice@example.com",
            "to": "bob@example.com"
        }
    }
"""
import datetime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.encoders import encode_base64
from email.utils import COMMASPACE, formatdate, make_msgid
import json
import mimetypes
import optparse
import os
import smtplib
import sys


def text_email(from_='',
               to=[],
               cc=None,
               bcc=None,
               subject='',
               body='',
               files=None,
               smtp_server='',
               smtp_port=25,
               smtp_username='',
               smtp_password=''):
    """ Generate a simple text email and send it to various recipients via an authenticated SMTP server.
    """
    message = MIMEMultipart()
    message['To'] = COMMASPACE.join(to)
    if cc:
        message['Cc'] = COMMASPACE.join(cc)
    message['From'] = from_
    message['Subject'] = subject
    message['Date'] = formatdate(localtime=True)
    message['Message-ID'] = make_msgid()
    # message.set_type('text/plain')
    message.attach(MIMEText(body))

    if files:
        for filepath in files:
            part = MIMEBase('application', 'octet-stream')
            mime_type = mimetypes.guess_type(filepath)[0]
            if mime_type:
                part.set_type(mime_type)

            part.set_payload(open(filepath, 'rb').read())
            encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filepath))
            message.attach(part)

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    if smtp_username:
        smtp.login(smtp_username, smtp_password)
    if cc:
        to += cc
    if bcc:
        to += bcc
    smtp.sendmail(from_, to, message.as_string())
    smtp.quit()


def main():
    path = os.path.expanduser('~/netrc.json')
    if not os.path.exists(path):
        print('Missing file: {}'.format(path))
        sys.exit()

    netrc = json.load(open(path, 'r'))

    parser = optparse.OptionParser()

    parser.add_option('-l',
                      '--label',
                      dest='label',
                      action='store',
                      type='string',
                      default='smtp',
                      help='netrc.json label [smtp]')

    parser.add_option('-s',
                      '--subject',
                      dest='subject',
                      action='store',
                      type='string',
                      default='',
                      help='email subject')

    parser.add_option('-b',
                      '--body',
                      dest='body',
                      action='store',
                      type='string',
                      default='',
                      help='email body')

    parser.add_option('-t',
                      '--to',
                      dest='to',
                      action='store',
                      type='string',
                      default='lcordier@gmail.com',
                      help='to addresses')

    options, args = parser.parse_args()

    label = options.label
    to = [address.strip() for address in (options.to or netrc.get(label, {}).get('to', '')).split(',')]
    subject = options.subject
    body = options.body

    text_email(
        from_=netrc.get(label, {}).get('from', ''),
        to=to,
        subject=subject,
        body=body,
        smtp_server=netrc.get(label, {}).get('host', ''),
        smtp_port=netrc.get(label, {}).get('port', ''),
        smtp_username=netrc.get(label, {}).get('username', ''),
        smtp_password=netrc.get(label, {}).get('password', ''),
        files=args
    )


if __name__ == '__main__':
    main()

