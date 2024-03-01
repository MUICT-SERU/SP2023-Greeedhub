#!/usr/bin/env python

""" Common password/passphrase functions.
"""
import hashlib
import os
import random


ALPHA_LOWER = 'abcdefghijklmnopqrstuvwxyz'
ALPHA_UPPER = ALPHA_LOWER.upper()
NUMERIC = '0123456789'
SPECIAL = '!@#$%^&*()-_=+{}[]|/.,<>'  # We ignore \'"

ROOT = os.path.dirname(os.path.abspath(__file__))
WORDS = [word.strip() for word in open(os.path.join(ROOT, 'wordlist.txt'), 'r').readlines() if word.strip()]


def generate_password(n=8, recipe=[6, 0, 1, 1], charsets=[ALPHA_LOWER, ALPHA_UPPER, NUMERIC, SPECIAL]):
    """ Create a password with a recipe.
    """
    rand = random.SystemRandom()
    ingredients = []
    for k, charset in zip(recipe, charsets):
        ingredients.extend(rand.choices(charset, k=k))

    return ''.join(rand.sample(ingredients, n))


def generate_memorable_password(n=6, words=WORDS):
    """ Create a password that is more memorable.
    """
    rand = random.SystemRandom()

    chars = list(rand.choice([word for word in words if len(word) == n]))
    idx = rand.randint(0, n - 1)
    chars[idx] = chars[idx].upper()

    pre = rand.choices(SPECIAL, k=1) + rand.choices(NUMERIC, k=1)
    post = rand.choices(SPECIAL, k=1) + rand.choices(NUMERIC, k=1)

    # This breaks the standard pattern, but potentially loose one each of (SPECIAL, NUMERIC).
    rand.shuffle(pre)
    rand.shuffle(post)

    source = pre + chars + post
    idx = rand.randint(0, 2)

    return ''.join(source[idx:idx + n + 2])


def generate_passphrase(n=3, recipe=[6, 5, 4], mode=1, words=WORDS):
    """ Create a passphrase that is more memorable.

        A passphrase is a sentencelike string of words used for authentication that
        is longer than a traditional password, easy to remember and difficult to crack.
    """
    rand = random.SystemRandom()

    ingredients = []
    for idx in range(n):
        r = recipe[idx % len(recipe)]
        ingredients.append(rand.choice([word for word in words if len(word) == r]))

    rand.shuffle(ingredients)

    # TitleCaseWords + 2 digits.
    if mode in [1]:
        return ''.join([ingredient.title() for ingredient in ingredients] + rand.choices(NUMERIC, k=2))

    # raNdom caPitaliZation.
    if mode in [2]:
        chars = list(''.join(ingredients))
        for _ in range(rand.randint(0, 3)):
            idx = rand.randint(0, len(chars) - 1)
            chars[idx] = chars[idx].upper()
        return ''.join(chars)

    # lowercasewords with random characters.
    if mode in [3]:
        extra = ''.join(rand.choices(NUMERIC + SPECIAL, k=2))
        ingredients.insert(rand.randint(0, len(ingredients)), extra)
        return ''.join(ingredients)

    raise ValueError('Invalid mode.')


if __name__ == '__main__':

    for i in range(10):
        print(generate_passphrase(mode=1))


