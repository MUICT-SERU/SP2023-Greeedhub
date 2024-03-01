from __future__ import print_function

import argparse
import importlib
import os
import sys
import verhawk.scanner
import verhawk.constants as constants


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('parent_package')
    parser.add_argument('-V', '--version',
        action='store_true',
        help='Display version information'),
    parser.add_argument('-e', '--exclude',
        action='append',
        default=[],
        help='Ignore sub-[package|module] by name.')
    parser.add_argument('-v', '--verbose',
        action='store_true',
        help='Show packages without version data.')
    parser.add_argument('-j', '--json',
        action='store_true',
        help='Emit JSON to stdout')
    parser.add_argument('-p', '--packages-only',
        action='store_true',
        help='Ignore non-packages (i.e modules)')
    parser.add_argument('-r', '--recursive',
        action='store_true',
        help='Descend into package looking for additional version data.')

    args = parser.parse_args()

    if args.version:
        print(verhawk.version.__version_long__)
        exit(0)

    try:
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            parent_package = importlib.import_module(args.parent_package)

        sys.stdout = constants.STDOUT
    except ImportError as e:
        print(e, file=sys.stderr)
        exit(1)

    scanner = verhawk.scanner.Scanner(parent_package, args.exclude,
                                     args.recursive, args.packages_only)

    if args.json:
        print(scanner.as_json())
    else:
        for pkg, version in sorted(scanner):
            if not args.verbose and version is None:
                continue

            print('{0}={1}'.format(pkg, version))

if __name__ == '__main__':
    main()
