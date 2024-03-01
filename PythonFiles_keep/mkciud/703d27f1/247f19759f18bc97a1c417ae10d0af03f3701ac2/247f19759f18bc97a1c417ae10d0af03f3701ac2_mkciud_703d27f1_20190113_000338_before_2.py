from . import UserData

import os
import sys


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
        userdata = UserData()
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
                filename = arg
                with open(filename, 'r') as f:
                    message_body = f.read()
                message_subtype = None
            userdata.add(message_body, message_subtype)
        userdata.export(sys.stdout.buffer)
        return 0
    except Exception as e:
        print_error(str(e))
        return -1
