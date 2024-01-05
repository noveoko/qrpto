from Crypto.Cipher import AES
from Crypto.PublicKey import ECC
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def combine_private_keys(keys):
    # Combine private keys using a simple XOR operation
    shared_secret = keys[0].to_bytes()
    for key in keys[1:]:
        shared_secret = bytes(a ^ b for a, b in zip(shared_secret, key.to_bytes()))
    return ECC.construct(curve='P-256', d=int.from_bytes(shared_secret, 'big'))

def generate_key_pair():
    # Generate an ECC key pair
    private_key = ECC.generate(curve='P-256')
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt(message, shared_secret):
    # Generate a random nonce for symmetric encryption
    nonce = get_random_bytes(16)
    
    # Derive a symmetric key from the shared secret using PBKDF2
    symmetric_key = PBKDF2(shared_secret.to_string(), nonce, dkLen=32, count=1000000, prf=lambda p, s: HMAC.new(s, p, SHA256).digest())

    # Use AES-GCM for symmetric encryption
    cipher = AES.new(symmetric_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(pad(message.encode(), AES.block_size))

    return ciphertext, nonce, tag

def decrypt(ciphertext, nonce, tag, private_keys):
    # Combine private keys to reconstruct the shared secret
    shared_secret = combine_private_keys(private_keys)

    # Derive a symmetric key from the shared secret using PBKDF2
    symmetric_key = PBKDF2(shared_secret.to_string(), nonce, dkLen=32, count=1000000, prf=lambda p, s: HMAC.new(s, p, SHA256).digest())

    # Use AES-GCM for symmetric decryption
    cipher = AES.new(symmetric_key, AES.MODE_GCM, nonce=nonce)
    decrypted_message = unpad(cipher.decrypt_and_verify(ciphertext, tag), AES.block_size)

    return decrypted_message.decode()

# Example usage
private_key_1, public_key_1 = generate_key_pair()
private_key_2, public_key_2 = generate_key_pair()
private_key_3, public_key_3 = generate_key_pair()

shared_secret = combine_private_keys([private_key_1, private_key_2, private_key_3])

message = "Your secret message"
ciphertext, nonce, tag = encrypt(message, shared_secret)

# Simulate sharing the decryption keys (private keys)
decryption_keys = [private_key_1, private_key_2]

# Simulate the decryption process
try:
    decrypted_message = decrypt(ciphertext, nonce, tag, decryption_keys)
    print(f"Decrypted message: {decrypted_message}")
except ValueError:
    print("Decryption failed. Not enough valid private keys.")