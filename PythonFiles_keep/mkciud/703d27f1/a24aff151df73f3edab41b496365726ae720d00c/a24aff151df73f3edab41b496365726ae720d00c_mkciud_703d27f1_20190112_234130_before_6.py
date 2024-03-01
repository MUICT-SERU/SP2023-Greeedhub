from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow, range, round, str, super, zip)
from future import standard_library
standard_library.install_aliases()


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gzip
import os
import sys


SUBTYPE_PREFIX_MAP={
    'cloud-boothook':       '#cloud-boothook\n',
    'cloud-config':         '#cloud-config\n',
    'cloud-config-archive': '#cloud-config-archive\n',
    'part-handler':         '#part-handler\n',
    'upstart-job':          '#upstart-job\n',
    'x-include-once-url':   '#include-once\n',
    'x-include-url':        '#include\n',
    'x-shellscript':        '#!',
}


OPT_SUBTYPE_MAP={
    '-cb':   'cloud-boothook',
    '-cc':   'cloud-config',
    '-cca':  'cloud-config-archive',
    '-ph':   'part-handler',
    '-uj':   'upstart-job',
    '-io':   'x-include-once-url',
    '-i':    'x-include-url',
    '-sh':   'x-shellscript',
}


def print_error(message):
    print('{0}: {1}'.format(os.path.basename(sys.argv[0]), message), file=sys.stderr)


def print_usage():
    print('usage: {0} [ [option] filename ]+'.format(os.path.basename(sys.argv[0])), file=sys.stderr)
    print('options:',                       file=sys.stderr)
    print('\t-cb    cloud-boothook',        file=sys.stderr)
    print('\t-cc    cloud-config',          file=sys.stderr)
    print('\t-cca   cloud-config-archive',  file=sys.stderr)
    print('\t-ph    part-handler',          file=sys.stderr)
    print('\t-uj    upstart-job',           file=sys.stderr)
    print('\t-io    x-include-once-url',    file=sys.stderr)
    print('\t-i     x-include-url',         file=sys.stderr)
    print('\t-sh    x-shellscript',         file=sys.stderr)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 0:
        print_usage()
        return 0

    try:
        multipart_message = MIMEMultipart()
        while args:
            arg = args.pop(0)
            if arg in OPT_SUBTYPE_MAP:
                if len(args) == 0:
                    print_usage()
                    return -1
                filename = args.pop(0)
                with open(filename, 'r') as f:
                    message_body = f.read()
                message_subtype = OPT_SUBTYPE_MAP[arg]
            else:
                # autodetect subtype
                filename = arg
                with open(filename, 'r') as f:
                    message_body = f.read()
                message_subtype = None
                for subtype, prefix in SUBTYPE_PREFIX_MAP.items():
                    if message_body.startswith(prefix):
                        message_subtype = subtype
                        break
                if not message_subtype:
                    print_error('could not determine file type: {0}'.format(filename))

            assert message_body
            assert message_subtype
            assert message_subtype in SUBTYPE_PREFIX_MAP

            # strip prefix where unnecessary
            prefix = SUBTYPE_PREFIX_MAP[message_subtype]
            if prefix.endswith('\n'):
                message_body = message_body[len(prefix):]

            multipart_message.attach(MIMEText(message_body, message_subtype))

        with gzip.GzipFile(fileobj=sys.stdout.buffer, mode='wb') as f:
            f.write(multipart_message.as_bytes())

        return 0
    except Exception as e:
        print_error(str(e))
        return -1
