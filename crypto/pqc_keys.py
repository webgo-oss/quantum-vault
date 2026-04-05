from pqcrypto.kem.ml_kem_768 import generate_keypair

def generate_keys():

    public_key, private_key = generate_keypair()

    with open("keys/public.key", "wb") as f:
        f.write(public_key)

    with open("keys/private.key", "wb") as f:
        f.write(private_key)

    print("Post-Quantum Keys Generated Successfully")