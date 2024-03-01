#!/usr/bin/env python

""" CLI IMAP tool.

    To configure this tool for a specific IMAP account, set the default values of:

      * options.host
      * options.username
      * options.password
"""
import email
import email.utils
from email.header import decode_header
import optparse
import os
import mailbox
import sys

import imapclient
from pyzmail import parse


def ensure_directory_exists(path, expand_user=True, file=False):
    """ Create a directory if it doesn't exists.

        Expanding '~' to the user's home directory on POSIX systems.
    """
    if expand_user:
        path = os.path.expanduser(path)

    if file:
        directory = os.path.dirname(path)
    else:
        directory = path

    if not os.path.exists(directory) and directory:
        try:
            os.makedirs(directory)
        except OSError as e:
            # A parallel process created the directory after the existance check.
            pass

    return(path)


def init_dump(path):
    """ Initialize a dump directory.
    """
    ensure_directory_exists(os.path.join(path, 'tmp'))
    ensure_directory_exists(os.path.join(path, 'cur'))
    ensure_directory_exists(os.path.join(path, 'new'))


def process_email(email_string):
    """ Extract details from email.
    """
    message = parse.email.message_from_string(email_string)
    try:
        from_name = parse.get_mail_addresses(message, 'from')[0][0]
    except IndexError:
        from_name = 'none'

    try:
        from_address = parse.get_mail_addresses(message, 'from')[0][1]
    except IndexError:
        from_address = 'none'

    header_parser = email.parser.HeaderParser()
    msg = header_parser.parsestr(email_string)
    headers = dict(msg.items())

    from_ = '{} <{}>'.format(from_name, from_address)
    subject = message['Subject']
    subject = decode_header(subject)[0][0]
    message_id = headers.get('Message-ID', '<missing>')

    return({'from': from_, 'subject': subject, 'message_id': message_id})


def main():
    parser = optparse.OptionParser()

    parser.add_option('-c',
                      '--command',
                      dest='command',
                      action='store',
                      type='string',
                      default='ls',
                      help='command')

    parser.add_option('-s',
                      '--source',
                      dest='source',
                      action='store',
                      type='string',
                      default='',
                      help='source folder')

    parser.add_option('-d',
                      '--destination',
                      dest='destination',
                      action='store',
                      type='string',
                      default='',
                      help='destination folder')

    parser.add_option('',
                      '--host',
                      dest='host',
                      action='store',
                      type='string',
                      default='',
                      help='IMAP host')

    parser.add_option('-u',
                      '--username',
                      dest='username',
                      action='store',
                      type='string',
                      default='',
                      help='IMAP username')

    parser.add_option('-p',
                      '--password',
                      dest='password',
                      action='store',
                      type='string',
                      default='',
                      help='IMAP password')

    options, args = parser.parse_args()

    host = options.host
    username = options.username
    password = options.password
    command = options.command
    src = options.source
    dst = options.destination

    valid_commands = ['ls', 'cp', 'mv', 'mkdir', 'rmdir', 'dump']

    if command not in valid_commands:
        print('Unknown commad: {}.'.format(command))
        print('Valid commands: {}.'.format(', '.join(valid_commands)))
        print('')
        parser.print_help()
        sys.exit()

    if command in ['cp', 'mv', 'mkdir', 'rmdir', 'dump'] and not src:
        print('Command: {} requires a source folder.'.format(command))
        print('')
        parser.print_help()
        sys.exit()

    if command in ['cp', 'mv'] and not dst:
        print('Command: {} requires a destination folder.'.format(command))
        print('')
        parser.print_help()
        sys.exit()

    with imapclient.IMAPClient(host) as server:
        server.login(username, password)
        server.select_folder('INBOX', readonly=True)
        folders = [rec[2] for rec in server.list_folders()]
        subscribed_folders = [rec[2] for rec in server.list_sub_folders()]
        server.close_folder()

        if command in ['ls']:
            if not src:
                for folder in sorted(folders):
                    print(folder)
            else:
                if src in folders:
                    server.select_folder(src)
                    messages = server.search('ALL')
                else:
                    print('Unknown folder: {}'.format(src))
                    sys.exit()

                for uid, message_data in server.fetch(messages, 'RFC822').items():
                    message_string = message_data[b'RFC822']

                    print(process_email(message_string))

        if command in ['cp']:
            if src in folders:
                server.select_folder(src)
                messages = server.search('ALL')
            else:
                print('Unknown folder: {}'.format(src))
                sys.exit()

            if dst not in folders:
                print('Unknown folder: {}'.format(dst))
                sys.exit()

            response = server.copy(messages, dst)
            server.close_folder()

        if command in ['mv']:
            if src in folders:
                server.select_folder(src)
                messages = server.search('ALL')
            else:
                print('Unknown folder: {}'.format(src))
                sys.exit()

            if dst not in folders:
                print('Unknown folder: {}'.format(dst))
                sys.exit()

            response = server.move(messages, dst)
            server.close_folder()

        if command in ['mkdir']:
            if server.folder_exists(src):
                print('Folder: {} already exists.'.format(src))
                sys.exit()

            server.select_folder('INBOX', readonly=True)
            server.create_folder(src)
            server.subscribe_folder(src)
            server.close_folder()

        if command in ['rmdir']:
            if server.folder_exists(src):
                if src.upper() != 'INBOX':
                    if src in subscribed_folders:
                        server.unsubscribe_folder(src)

                    server.select_folder('INBOX', readonly=True)
                    server.delete_folder(src)
                    server.close_folder()
                else:
                    print('Cannot delete folder: INBOX')
                    sys.exit()

        if command in ['dump']:
            if src in folders:
                server.select_folder(src)
                messages = server.search('ALL')
            else:
                print('Unknown folder: {}'.format(src))
                sys.exit()

            maildir = mailbox.Maildir(dst)
            init_dump(dst)
            try:
                for uid, message_data in server.fetch(messages, 'RFC822').items():
                    message_string = message_data[b'RFC822']
                    try:
                        maildir.add(message_string)
                    except:
                        raise
                        email_message = email.message_from_string(message_string)
                        error = 'ERROR: From: {}, Subject: {}.'.format(email_message.get('From'), email_message.get('Subject'))
                        print(error)
            finally:
                maildir.flush()
                maildir.close()

            server.close_folder()


if __name__ == '__main__':
    main()
