#!/usr/bin/env python
from __future__ import print_function
import json
import os
import pkgutil
import sys


STDERR, STDOUT = sys.stderr, sys.stdout


class VersionScanner(object):
    def __init__(self, package, exclusions=[], recursive=False, packages_only=False):
        self.package = package
        self.prefix = self.package.__name__ + '.'
        self.exclusions = exclusions
        self.versions = dict()
        self.recursive = recursive
        self.packages_only = packages_only
        self.scan()

    def __iter__(self):
        for k, v in self.versions.items():
            yield k, v

    def scan(self):


        try:
            module = self.package
            modname = module.__name__

            try:
                self.versions[modname] = module.__version__ or module.version or module._version
            except AttributeError:
                self.versions[modname] = None
        except ImportError as e:
            print('ImportError({0}): {1}'.format(modname, e), file=sys.stderr)

        if self.recursive:
            try:
                for importer, modname, ispkg in pkgutil.iter_modules(self.package.__path__, self.prefix):
                    excluded = False
                    for ex in self.exclusions:
                        ex = self.prefix + ex
                        if modname == ex:
                            excluded = True
                            break

                    if excluded:
                        continue

                    if self.packages_only and not ispkg:
                        continue

                    try:
                        module = None
                        with open(os.devnull, 'w') as devnull:
                            sys.stdout = devnull
                            module = importer.find_module(modname).load_module(modname)

                        sys.stdout = STDOUT

                        try:
                            self.versions[modname] = module.__version__
                        except AttributeError:
                            self.versions[modname] = None

                    except ImportError as e:
                        print('ImportError({0}): {1}'.format(modname, e), file=sys.stderr)

            except AttributeError:
                # has no sub-packages or sub-modules, so ignore
                pass
            except TypeError:
                # has strange requirements at import-time, so ignore
                pass

    def as_json(self):
        return json.dumps(self.versions, sort_keys=True)


    def as_zip(self):
        return zip(self.versions.keys(), self.versions.values())


if __name__ == '__main__':
    import argparse
    import importlib


    parser = argparse.ArgumentParser()
    parser.add_argument('parent_package')
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

    try:
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            parent_package = importlib.import_module(args.parent_package)

        sys.stdout = STDOUT
    except ImportError as e:
        print(e, file=sys.stderr)
        exit(1)

    scanner = VersionScanner(parent_package, args.exclude, args.recursive, args.packages_only)


    if args.json:
        print(scanner.as_json())
    else:
        for pkg, version in sorted(scanner):
            if not args.verbose and version is None:
                continue

            print('{0}={1}'.format(pkg, version))

