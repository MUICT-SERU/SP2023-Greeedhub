from importlib import import_module
from glob import glob
import os
import json


for profile in glob('profiles/*.json'):
    profile_name = os.path.basename(profile)
    packages = json.load(open(profile))

    functions = []

    for package_name in packages:
        package = import_module(package_name)
        exports = package.__dict__.keys()

        functions.append((package_name, None, repr(package)))

        for key in exports:
            if key.startswith('_'):
                continue

            representation = repr(getattr(package, key))
            functions.append((package_name, key, representation))

    json.dump(functions, open('profiles/build/{}'.format(profile_name), 'w'))