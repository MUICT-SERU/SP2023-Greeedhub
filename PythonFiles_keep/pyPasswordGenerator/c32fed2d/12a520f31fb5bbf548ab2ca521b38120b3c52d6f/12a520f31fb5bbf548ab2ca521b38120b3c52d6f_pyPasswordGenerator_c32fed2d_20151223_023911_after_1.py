import random

def comprobarLetra(letra, passphrase):
    for i in range(len(passphrase)):
        if passphrase[i] == letra:
            return True
    return False

def generarPass(size):
    passphrase = ""
    abecedario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    i = 0
    while i < size:
        if len(passphrase) == (len(abecedario)-1):
            print("Alcanzado el límite", size)
            return passphrase
        
        letrita = abecedario[random.randrange(len(abecedario))]
        if not comprobarLetra(letrita, passphrase):
            passphrase += letrita
            i += 1
    
    return passphrase

if __name__ == '__main__':
    print(generarPass(500))
            