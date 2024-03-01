from random import randrange

def verifyLetter(letter, passphrase):
    for i in range(len(passphrase)):
        if passphrase[i] == letter:
            return True
    return False

def generate(size):
    passphrase = ""
    vocals = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    numbers = "0123456789"
    simbols = "#./^+-_"

    vocabulary = vocals + consonants + numbers + vocals.upper() + simbols + consonants.upper()

    i = 0
    while i < size:
        if len(passphrase) == (len(vocabulary)-1):
            print("Alcanzado el límite", len(passphrase))
            return passphrase

        letter = vocabulary[randrange(len(vocabulary))]
        if not verifyLetter(letter, passphrase):
            passphrase += letter
            i += 1

    return passphrase

if __name__ == '__main__':
    print(generate(500))
