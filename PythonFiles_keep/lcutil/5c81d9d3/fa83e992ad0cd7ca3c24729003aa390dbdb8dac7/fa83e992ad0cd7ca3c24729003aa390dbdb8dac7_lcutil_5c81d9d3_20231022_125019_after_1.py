#!/usr/bin/env python

""" Common password/passphrase functions.

    https://en.wikipedia.org/wiki/Password_strength
    https://explainxkcd.com/wiki/index.php/936:_Password_Strength

    https://blog.jgc.org/2010/12/write-your-passwords-down.html
    https://en.wikipedia.org/wiki/Tabula_recta
    http://yannesposito.com/Scratch/en/blog/Password-Management/
    https://www.borderwallets.com/docs/the-solution

    https://www.netmux.com/blog/one-time-grid

    https://en.wikipedia.org/wiki/Diceware
    https://theworld.com/~reinhold/diceware.html
    https://arstechnica.com/information-technology/2014/03/diceware-passwords-now-need-six-random-words-to-thwart-hackers/
    https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
    https://diceware.dmuth.org/
    https://theworld.com/%7Ereinhold/dicewarekit.html
    https://github.com/agreinhold/Diceware-word-lists

Why diceware?

Which is more memorable? Da6ee^ch.aij or mock omen laugh weary dy glen?

The entropy offered by Diceware is 12.9 bits per word - log2(7776) - so the six-word passphrase above has an entropy of 77.4 bits.

Compare this to choosing 10 letters at random: the entropy of that is 10 * log2(26) = 47.0 bits.

If you were to use ASCII printable characters, you'd need at least 12 characters to surpass a six word memorable diceware password.

Diceware is a method for creating passphrases, passwords, and other cryptographic variables using an ordinary die from a pair of dice as a hardware random number generator. For each word in the passphrase, five rolls of the dice are required. The numbers from 1 to 6 that come up in the rolls are assembled as a five digit number, e.g. 43146. That number is then used to look up a word in a word list.


openssl rand -hex 20
openssl rand -base64 20
gpg --gen-random --armor 1 20

https://superuser.com/questions/137957/how-to-convert-aspell-dictionary-to-simple-list-of-words
aspell -d en dump master | aspell -l en expand | grep -v "'" |sort > wordlist_aspell_english.txt

https://www.kali.org/tools/wordlists/
https://packetstormsecurity.com/crackers/wordlists
https://www.hackingarticles.in/wordlists-for-pentester/
https://www.kaggle.com/datasets/taranvee/bruteforce-database-password-dictionaries


"""
import hashlib
import os
import random
import string


ALPHA_LOWER = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
ALPHA_UPPER = string.ascii_uppercase  # ALPHA_LOWER.upper()
NUMERIC = string.digits  # '0123456789'
SPECIAL = string.punctuation  # '!@#$%^&*()-_=+{}[]|/.,<>'  # We ignore \'"

ROOT = os.path.dirname(os.path.abspath(__file__))
WORDS = [word.strip() for word in open(os.path.join(ROOT, 'wordlists', 'wordlist.txt'), 'r').readlines() if word.strip()]


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
        print(generate_passphrase(mode=2))


