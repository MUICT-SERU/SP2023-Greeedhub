#!/usr/bin/env python

""" Functiuons for sending emails.

    html_email deals correctly with attachments and inline images as used by MS Exchange and Thunderbird.
"""
import datetime
from email.encoders import encode_base64
from email.header import decode_header
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.parser import HeaderParser
from email.utils import COMMASPACE, formatdate, make_msgid, parsedate
import json
import logging
import logging.config
import mimetypes
import os
import smtplib
import sys
import tempfile
import time

from util_fs import ensure_directory_exists, valid_filename

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

mimetypes.init()

try:
    from pyzmail import parse
except ImportError:
    pass
else:
    def strip_header(email_string):
        """ Remove content-description/type/disposition header.
        """
        lines = email_string.splitlines()
        try:
            while lines[0].strip() != '':
                lines.pop(0)
        except IndexError:
            pass

        return('\n'.join(lines[1:]))


    def extract_email_parts(email_string, dst=None, flatten=True, ascii=True):
        """ Process an email, extract meta data, bodies and attachments.
            The email can then be further processed with os.walk().
        """
        message = parse.email.message_from_string(email_string)

        from_ = parse.get_mail_addresses(message, 'from')
        to = parse.get_mail_addresses(message, 'to')

        # NOTE: parsedate don't take timezone into account!!!
        # https://stackoverflow.com/questions/1790795/parsing-date-with-timezone-from-an-email
        timestamp = datetime.datetime.fromtimestamp(time.mktime(parsedate(message['Date'])))

        subject = message['Subject']
        subject = decode_header(subject)[0][0]

        if ascii:
            subject = subject.decode('ascii', 'ignore')
            subject = ' '.join(subject.splitlines()).strip()

        header_parser = HeaderParser()
        msg = header_parser.parsestr(email_string)
        headers = dict(msg.items())
        message_id = headers.get('Message-ID', '<missing>')

        logger.info('message_id: ' + message_id)
        logger.info('subject: ' + subject)

        meta = {
            'from': from_,
            'to': to,
            'timestamp': timestamp.strftime('%Y%m%dT%H%M%S'),
            'subject': subject,
            'message_id': message_id,
        }

        parts = parse.get_mail_parts(message)
        if dst is None:
            dst = tempfile.mkdtemp()
        else:
            ensure_directory_exists(dst)

        dst_filename = valid_filename(os.path.join(dst, 'meta.json'))
        logger.info('meta: ' + dst_filename)
        with open(dst_filename, 'wb') as f:
            json.dump(meta, f)

        for part in parts:
            filename = part.filename
            type_ = part.type.lower()

            if type_ in ['message/rfc822']:
                if flatten:
                    extract_email_parts(strip_header(part.get_payload()), dst=dst, flatten=flatten, ascii=ascii)
                else:
                    extract_email_parts(strip_header(part.get_payload()), dst=os.path.join(dst, filename), flatten=flatten, ascii=ascii)

            elif type_ in ['text/html', 'text/plain'] and part.disposition not in ['attachment']:
                ext = {'text/html': '.html', 'text/plain': '.txt'}[type_]
                dst_filename = valid_filename(os.path.join(dst, 'body' + ext))
                logger.info('body: ' + dst_filename)
                with open(dst_filename, 'wb') as f:
                    f.write(part.get_payload())

            elif part.disposition in ['attachment']:
                dst_filename = valid_filename(os.path.join(dst, filename), ascii=ascii)
                logger.info('attachment: ' + dst_filename)
                with open(dst_filename, 'wb') as f:
                    f.write(part.get_payload())
        return dst


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


def html_email(from_='',
               to=[],
               cc=None,
               bcc=None,
               subject='',
               text_body='',
               html_body='',
               files=None,
               images=[],
               smtp_server='',
               smtp_port=25,
               smtp_username='',
               smtp_password=''):
    """ Generate a HTML email and send it to various recipients via an authenticated SMTP server.

        +-------------------------------------------------------+
        | multipart/mixed                                       |
        |                                                       |
        |  +-------------------------------------------------+  |
        |  |   multipart/related                             |  |
        |  |                                                 |  |
        |  |  +-------------------------------------------+  |  |
        |  |  | multipart/alternative                     |  |  |
        |  |  |                                           |  |  |
        |  |  |  +-------------------------------------+  |  |  |
        |  |  |  | text can contain [cid:logo.png]     |  |  |  |
        |  |  |  +-------------------------------------+  |  |  |
        |  |  |                                           |  |  |
        |  |  |  +-------------------------------------+  |  |  |
        |  |  |  | html can contain src="cid:logo.png" |  |  |  |
        |  |  |  +-------------------------------------+  |  |  |
        |  |  |                                           |  |  |
        |  |  +-------------------------------------------+  |  |
        |  |                                                 |  |
        |  |  +-------------------------------------------+  |  |
        |  |  | image logo.png  "inline" attachement      |  |  |
        |  |  +-------------------------------------------+  |  |
        |  |                                                 |  |
        |  +-------------------------------------------------+  |
        |                                                       |
        |  +-------------------------------------------------+  |
        |  | pdf ("download" attachment, not inline)         |  |
        |  +-------------------------------------------------+  |
        |                                                       |
        +-------------------------------------------------------+

        see: https://www.anomaly.net.au/blog/constructing-multipart-mime-messages-for-sending-emails-in-python/
    """
    message = MIMEMultipart('mixed')

    del message['sender']
    del message['errors-to']
    message['To'] = COMMASPACE.join(to)
    if cc:
        message['Cc'] = COMMASPACE.join(cc)
    message['From'] = from_
    message['Subject'] = subject
    message['Date'] = formatdate(localtime=True)
    message['Message-ID'] = make_msgid()
    message.epilogue = ''

    body = MIMEMultipart('alternative')

    text_part = MIMEText(text_body, 'plain')
    # text_part.set_type('text/plain')
    # text_part.set_charset('iso-8859-1')
    # text_part.replace_header('Content-Transfer-Encoding', 'quoted-printable')
    body.attach(text_part)

    html_part = MIMEText(html_body, 'html')
    body.attach(html_part)

    related = MIMEMultipart('related')
    related.attach(body)

    for count, image in enumerate(images, 1):
        if isinstance(image, basestring):
            with open(image, 'rb') as image_file:
                image_data = image_file.read()
            image_part = MIMEImage(image_data)
            image_filename = os.path.basename(image)
        elif isinstance(image, (tuple)):
            image_part = MIMEImage(image[1])
            image_filename = image[0]

        mime_type = mimetypes.guess_type(image_filename)[0]
        if mime_type:
            image_part.set_type(mime_type)

        image_part.add_header('Content-Location', image_filename)
        image_part.add_header('Content-Disposition', 'inline', filename=image_filename)
        image_part.add_header('Content-ID', '<image{}>'.format(count))
        related.attach(image_part)

    message.attach(related)

    if files:
        for attachment in files:
            part = MIMEBase('application', 'octet-stream')  # 'octet-stream' filtered by MS Exchange.
            with open(attachment, 'rb') as attachment_file:
                attachment_data = attachment_file.read()

            mime_type = mimetypes.guess_type(attachment)[0]
            if mime_type:
                part.set_type(mime_type)

            part.set_payload(attachment_data)
            encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment))
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


if __name__ == '__main__':

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'stream': 'ext://sys.stdout',
            }
        },
        'formatters': {
            'detailed': {
                'format': '%(asctime)s %(module)-17s line:%(lineno)-4d %(levelname)-8s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            }
        }
    })

    ascii = len(sys.argv) > 1 and sys.argv[1].lower() == 'ascii'
    extract_email_parts(sys.stdin.read(), ascii=ascii)
