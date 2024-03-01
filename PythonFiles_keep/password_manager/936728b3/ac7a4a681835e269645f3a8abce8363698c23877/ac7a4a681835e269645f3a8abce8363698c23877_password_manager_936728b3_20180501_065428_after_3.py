from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from zipfile import ZipFile
import os
import json
from threading import Timer


class Vault:
    def __init__(self, password, path_to_vault='password.vault', timeout=60):
        self.password = password
        self.path_to_vault = path_to_vault
        self.timeout = timeout
        self.data = dict()
        self.timer = Timer(timeout, self.invalidate_data)
        self.timer.start()
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'data'):
            self.save()
        self.timer.cancel()

    def set_data_with_timer(self, data=None):
        if data is not None:
            self.data = data
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.invalidate_data)
        self.timer.start()

    def invalidate_data(self):
        self.save()
        del self.data

    def __iter__(self):
        return self.data

    def __setitem__(self, key, value):
        if 'password' not in value.keys():
            raise ValueError('At least, password must be set.')

        self.data[key] = value
        self.set_data_with_timer()

    def __getitem__(self, item):
        return self.data[item]

    def load(self):
        if not os.path.exists(self.path_to_vault):
            key = RSA.generate(2048)
            encrypted_key = key.export_key(passphrase=self.password, pkcs=8,
                                           protection="scryptAndAES128-CBC")

            with ZipFile(self.path_to_vault, 'w') as vault:
                with vault.open('master.bin', 'w') as f:
                    f.write(encrypted_key)

            return self.set_data_with_timer(dict())
        else:
            with ZipFile(self.path_to_vault) as vault:
                with vault.open('master.bin', 'r') as f:
                    key = RSA.import_key(f.read(), passphrase=self.password)
                try:
                    with vault.open('password.bin', 'r') as f:
                        enc_session_key, nonce, tag, ciphertext = \
                            [f.read(x) for x in (key.size_in_bytes(), 16, 16, -1)]
                        cipher_rsa = PKCS1_OAEP.new(key)
                        session_key = cipher_rsa.decrypt(enc_session_key)
                        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
                        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
                        return self.set_data_with_timer(json.loads(data.decode()))
                except KeyError:
                    return self.set_data_with_timer(dict())

    def save(self):
        with ZipFile(self.path_to_vault) as vault:
            with vault.open('master.bin') as f:
                master_bin = f.read()
        with ZipFile(self.path_to_vault, 'w') as vault:
            with vault.open('master.bin', 'w') as f:
                f.write(master_bin)
            with vault.open('password.bin', 'w') as f:
                key = RSA.import_key(master_bin, passphrase=self.password)
                session_key = get_random_bytes(16)
                cipher_rsa = PKCS1_OAEP.new(key)
                enc_session_key = cipher_rsa.encrypt(session_key)
                cipher_aes = AES.new(session_key, AES.MODE_EAX)
                ciphertext, tag = cipher_aes.encrypt_and_digest(json.dumps(self.data).encode())
                for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
                    f.write(x)

    def change_master_key(self, old_password, new_password):
        if old_password == self.password:
            with ZipFile(self.path_to_vault) as vault:
                with vault.open('master.bin', 'r') as f:
                    master_bin = f.read()
            with ZipFile(self.path_to_vault, 'w') as vault:
                with vault.open('master.bin', 'w') as f:
                    f.write(master_bin)
                with vault.open('password.bin', 'w') as f:
                    key = RSA.import_key(master_bin, passphrase=new_password)
                    session_key = get_random_bytes(16)
                    cipher_rsa = PKCS1_OAEP.new(key)
                    enc_session_key = cipher_rsa.encrypt(session_key)
                    cipher_aes = AES.new(session_key, AES.MODE_EAX)
                    ciphertext, tag = cipher_aes.encrypt_and_digest(json.dumps(self.data).encode())
                    for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
                        f.write(x)
