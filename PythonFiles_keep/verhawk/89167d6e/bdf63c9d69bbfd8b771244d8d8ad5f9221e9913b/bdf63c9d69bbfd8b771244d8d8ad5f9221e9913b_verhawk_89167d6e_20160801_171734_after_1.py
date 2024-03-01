#!/usr/bin/env python
from __future__ import print_function
import json
import pkgutil
import sys
from pprint import pprint


class VersionScanner(object):
    def __init__(self, package, exclusions=[]):
        self.package = package
        self.prefix = self.package.__name__ + '.'
        self.exclusions = exclusions
        self.versions = dict()
        self.scan()
        

    def __iter__(self):
        for k, v in self.versions.items():
            yield k, v

    
    def scan(self):
        try:
            module = self.package
        
            try:
                self.versions[module.__name__] = module.__version__
            except AttributeError:
                self.versions[module.__name__] = 'unknown'
        except ImportError as e:
            print('ImportError({0}): {1}'.format(module.__name__, e), file=sys.stderr)

        for importer, modname, ispkg in pkgutil.iter_modules(self.package.__path__, self.prefix):
            excluded = False
            for ex in self.exclusions:
                ex = self.prefix + ex
                if modname == ex:
                    excluded = True 
                    break
    
            if excluded:
                continue
    
            try:
                module = importer.find_module(modname).load_module(modname)
        
                try:
                    self.versions[modname] = module.__version__
                except AttributeError:
                    self.versions[modname] = 'unknown'
            except ImportError as e:
                print('ImportError({0}): {1}'.format(modname, e), file=sys.stderr)

    def as_json(self):
        return json.dumps(self.versions, sort_keys=True)


    def as_zip(self):
        return zip(self.versions.keys(), self.versions.values())


if __name__ == '__main__':
    import argparse
    import importlib


    parser = argparse.ArgumentParser()
    parser.add_argument('parent_package')
    parser.add_argument('-e', '--exclude', action='append', default=[])
    parser.add_argument('-j', '--json', action='store_true')

    args = parser.parse_args()
    parent_package = importlib.import_module(args.parent_package)
    scanner = VersionScanner(parent_package, args.exclude)


    if args.json:
        print(scanner.as_json())
    else:
        for pkg, version in sorted(scanner):
            print('{0}={1}'.format(pkg, version))
