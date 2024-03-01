import os


# head :: [a] -> a
def head(xs):
    return xs[0]


# last :: [a] -> a
def last(xs):
    return xs[-1]


# init :: [a] -> [a]
def init(xs):
    return xs[:-1]


# get_extension_from :: String -> String
def get_extension_from(filename):
    return last(filename.split('.')) if '.' in filename else ''


# is_number :: String -> Boolean
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# remove_extension_from :: String -> String
def remove_extension_from(filename):
    if last(filename) is '.':
        return filename
    path, ext = os.path.splitext(filename)
    return path if not (filename == path) else \
        '' if path.startswith('.') else path


# remove_extension_from :: String -> String
def remove_revision_suffix_from(filename):
    parts = filename.split('#')
    if len(parts) == 1:
        return filename
    if len(parts) == 2:
        return head(parts) \
            if '' not in parts and is_number(last(parts)) else '#'.join(parts)
    return '#'.join(init(parts)) \
        if not last(parts) is '' else '#'.join(init(parts)) + '#'


# append_suffix_to :: String -> Integer -> String
def append_suffix_to(string, increment=1):
    inc = '{:03d}'.format(increment)
    return '{}#{}'.format(string, str(inc))


# suggest_new_filename :: (String, Function, String) -> String
def suggest_new_filename(filename, predicate=None, suggested_suffix=1):
    name = remove_revision_suffix_from(remove_extension_from(filename))
    extension = get_extension_from(filename)
    extension = '.{}'.format(extension) if extension else ''
    suggestion = append_suffix_to(name, suggested_suffix) + extension
    return suggestion if not predicate or not predicate(suggestion) else \
        suggest_new_filename(filename, predicate, suggested_suffix + 1)
