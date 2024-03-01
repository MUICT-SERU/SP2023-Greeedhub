""" Functiuons for sending emails.

    html_email deals correctly with attachments and inline images as used by MS Exchange and Thunderbird.
"""
from email.encoders import encode_base64
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.utils import COMMASPACE, formatdate, make_msgid
import smtplib


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

        # mime_type = mimetypes.guess_type(image_filename)[0]
        # if mime_type:
        #     image_part.set_type(mime_type)

        image_part.add_header('Content-Location', image_filename)
        image_part.add_header('Content-Disposition', 'inline', filename=image_filename)
        image_part.add_header('Content-ID', '<image{}>'.format(count))
        related.attach(image_part)

    message.attach(related)

    if files:
        for attachment in files:
            # We need mimetypes here, only deal with PDFs at the moment.
            part = MIMEBase('application', 'pdf')  # 'octet-stream' filtered by MS Exchange.
            with open(attachment, 'rb') as attachment_file:
                attachment_data = attachment_file.read()

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
