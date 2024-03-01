from __future__ import print_function
import json
import os
import pkgutil
import sys
from . import constants


class Scanner(object):
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

                        sys.stdout = constants.STDOUT

                        try:
                            self.versions[modname] = module.__version__ or module.version or module._version
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


