### A work in progress validation rules ###
### rules strings are included in the file because it's convenient :D ###
import re

messages = {
    "required": u"{0} is required",
    "email": u"{0} is not a valid email",
    "min": u"{0} must be more than {1} characters",
    "mind": u"{0} must be higher than {1}",
    "max": u"{0} must be less than {1} characters",
    "maxd": u"{0} must be lower than {1}",
    "between": u"{0}'s length must be between {1} and {2} characters",
    "betweend": u"{0}'s value must be higher than {1} and lower than {2}",
}

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def required(value):
    return not len(str(value).strip()) == 0

def email(value):
    pattern = "^[a-z0-9]+([._-][a-z0-9]+)*@([a-z0-9]+([._-][a-z0-9]+))+$"
    if not re.match(pattern, value.strip()):
        return False

    return True

### min, validates if a string size is higher than the max constraint ###
### min, validates if a numerical value is higher than the min constraint ###
def min(value, constraint = None):

    try:
        constraint = float(constraint)
    except ValueError:
        raise ValueError('constraint is missing')
    except TypeError:
        raise TypeError('constraint is not a valid integer')
    
    if is_number(value):
        return float(value) >= constraint
    
    return len(value.strip()) >= constraint

### max, validates if a string size is lower than the max constraint ###
### max, validates if a numerical value is lower than the max constraint ###
def max(value, constraint = None):

    try:
        constraint = float(constraint)
    except ValueError:
        raise ValueError('constraint is missing')
    except TypeError:
        raise TypeError('constraint is not a valid integer')
    
    if is_number(value):
        return float(value) <= constraint
    
    return len(value.strip()) <= constraint

### between, validates if a string size is between 2 length ###
### between, validates if a numerical value is between 2 values ###
def between(value, constraint = None):
    if not constraint:
        raise ValueError('constraints are missing from the validation rule')

    try:
        constraints = constraint.split(',')
    except TypeError:
        raise TypeError('constraints are not a valid integer')

    if len(constraints) < 2:
        raise ValueError('constraints are missing from the validation rule')

    lower = float(constraints[0])
    higher = float(constraints[1])
    
    if is_number(value):
        return lower <= float(value) <= higher
    
    return lower <= len(value.strip()) <= higher