from random import randrange

def verifyLetter(letter, passphrase):
    for i in range(len(passphrase)):
        if passphrase[i] == letter:
            return False
    return True

def makeVocabulary(mixVocabulary):
        vocals = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"
        numbers = "0123456789"
        specials = "#./^+-_@"

        mixVocabulary = str(mixVocabulary)

        if mixVocabulary[0] == "@": vocabulary = mixVocabulary[1:]

        if len(vocabulary) == 0:
            vocabulary += vocals if mixVocabulary.count("a") or mixVocabulary.count("v") else ""
            vocabulary += vocals.upper() if mixVocabulary.count("a") or mixVocabulary.count("V") else ""
            vocabulary += consonants if mixVocabulary.count("a") or mixVocabulary.count("c") else ""
            vocabulary += consonants.upper() if mixVocabulary.count("a") or mixVocabulary.count("C") else ""
            vocabulary += numbers if mixVocabulary.count("a") or mixVocabulary.count("n") else ""
            vocabulary += specials if mixVocabulary.count("a") or mixVocabulary.count("s") else ""
            # vocabulary += vocals + consonants + numbers + vocals.upper() + specials + consonants.upper()

        return vocabulary

def generate(size, repeatCharacters=True, mixVocabulary="a"):
    """
        a -> All (lower/upper-case vocals, lower/upper-case consonants, numbers and specials)
        v -> Only lower-case vocals
        V -> Only upper-case vocals
        c -> Only lower-case consonants
        C -> Only upper-case consonants
        n -> Only numbers
        s -> Only specials

        It's possible to use combinations, for example:
            Cn -> Only upper-case consonants and numbers.
        If you want to use your own vocabulary, you will type '@' at start of parameter, for example:
                @bXcD3 -> Only will be used the characters b, X, c, D and 3.
    """
    passphrase = ""
    vocabulary = makeVocabulary(mixVocabulary)

    i = 0
    while i < size:
        if len(passphrase) == (len(vocabulary)-1) and not repeatCharacters:
            print("Alcanzado el límite", len(passphrase))
            return passphrase

        letter = vocabulary[randrange(len(vocabulary))]
        letterVerified = True if repeatCharacters else verifyLetter(letter, passphrase)

        if letterVerified:
            passphrase += letter
            i += 1

    return passphrase

if __name__ == '__main__':
    print(generate(100))
