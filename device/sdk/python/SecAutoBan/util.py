import sys
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def aes_cfb_encrypt(key: bytes, iv: bytes, plain_content: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
    return cipher.encrypt(plain_content)

def aes_cfb_decrypt(key: bytes, iv: bytes, cipher_content: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
    return cipher.decrypt(cipher_content)

def random_bytes():
    return get_random_bytes(16)

def print(s: str):
    sys.stdout.write(time.strftime("%Y-%m-%d %H:%M:%S\t", time.localtime()) + s + "\n")
    sys.stdout.flush()
