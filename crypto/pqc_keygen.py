from pqcrypto.kem.ml_kem_768 import generate_keypair
from security.key_protection import encrypt_private_key
import os

def generate_keys():

    print("Generating Post-Quantum keys...")

    public_key, private_key = generate_keypair()

    password = input("Create master password: ")

    encrypted_private, nonce = encrypt_private_key(private_key, password)

    os.makedirs("keys", exist_ok=True)

    with open("keys/public.key", "wb") as f:
        f.write(public_key)

    with open("keys/private.key.enc", "wb") as f:
        f.write(nonce + encrypted_private)

    print("Keys generated successfully")