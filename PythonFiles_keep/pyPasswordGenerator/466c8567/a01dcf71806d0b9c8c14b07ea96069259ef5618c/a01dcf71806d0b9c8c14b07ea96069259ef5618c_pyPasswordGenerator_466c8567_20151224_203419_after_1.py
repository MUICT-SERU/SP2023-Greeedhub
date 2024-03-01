from random import randrange

def verifyLetter(letter, passphrase):
    for i in range(len(passphrase)):
        if passphrase[i] == letter:
            return False
    return True

def generate(size, repeatCharacters=True):
    passphrase = ""
    vocals = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    numbers = "0123456789"
    simbols = "#./^+-_"

    vocabulary = vocals + consonants + numbers + vocals.upper() + simbols + consonants.upper()

    i = 0
    while i < size:
        if len(passphrase) == (len(vocabulary)-1) and not repeatCharacters:
            print("Alcanzado el límite", len(passphrase))
            return passphrase

        letter = vocabulary[randrange(len(vocabulary))]
        letterVerified = True if repeatCharacters else verifyLetter(letter)

        if letterVerified and repeatCharacters:
            passphrase += letter
            i += 1

    return passphrase

if __name__ == '__main__':
    print(generate(100))
