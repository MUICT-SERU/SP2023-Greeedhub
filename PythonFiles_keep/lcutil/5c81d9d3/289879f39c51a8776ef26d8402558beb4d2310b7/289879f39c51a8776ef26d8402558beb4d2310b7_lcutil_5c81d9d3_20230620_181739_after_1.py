#!/usr/bin/env python

""" Common password/passphrase functions.
"""
import hashlib
import random


ALPHA_LOWER = 'abcdefghijklmnopqrstuvwxyz'
ALPHA_UPPER = ALPHA_LOWER.upper()
NUMERIC = '0123456789'
SPECIAL = '!@#$%^&*()-_=+{}[]|/.,<>'  # We ignore '\'.


_luhn_transform = lambda digit: sum(divmod(digit * 2, 10))


def calculate_luhn(digits):
    """ Returns the Luhn checksum of a sequence of digits.
    """
    digits = list(map(int, digits))
    odds = digits[-2::-2]
    evens = digits[-1::-2]

    return sum(list(map(_luhn_transform, odds)) + evens) % 10


def validate_luhn(digits):
    """ Validate a sequence of digits (including checksum).
    """
    return calculate_luhn(digits) == 0


def checksum_luhn(digits):
    """ Calculate the Luhn checksum digit for a sequence of digits.

        http://en.wikipedia.org/wiki/Luhn_algorithm
    """
    return (10 - calculate_luhn(digits + '0')) % 10



def generate_password(n=8, recipe=[6, 0, 1, 1], charsets=[ALPHA_LOWER, ALPHA_UPPER, NUMERIC, SPECIAL]):
    """ Create a password with a recipe.
    """
    rand = random.SystemRandom()
    ingredients = []
    for k, charset in zip(recipe, charsets):
        # ingredients.extend(rand.sample(charset, k))
        ingredients.extend(rand.choices(charset, k=k))

    #rand.shuffle(ingredients)
    return ''.join(rand.sample(ingredients, n))


if __name__ == '__main__':
    print(generate_password())

