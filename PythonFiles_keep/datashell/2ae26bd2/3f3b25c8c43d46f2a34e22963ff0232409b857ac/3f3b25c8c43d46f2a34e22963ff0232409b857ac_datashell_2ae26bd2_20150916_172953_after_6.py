from importlib import import_module
import json


PACKAGES = [
    'numpy',
    'sympy',
    'pandas',
    'scipy.optimize',
    'scipy.stats',
    'scipy.stats.contingency',
    'scipy.stats.distributions',
    'statsmodels.api',
    'statsmodels.formula.api',
]


functions = []


for package_name in PACKAGES:
    package = import_module(package_name)
    exports = package.__dict__.keys()

    functions.append((package_name, None, repr(package)))

    for key in exports:
        if key.startswith('_'):
            continue

        representation = repr(getattr(package, key))
        functions.append((package_name, key, representation))


functions.extend([('sympy', letter, letter) for letter in 'a b c d e o p q r s u v w x y z'.split()])

json.dump(functions, open('helpers.json', 'w'))