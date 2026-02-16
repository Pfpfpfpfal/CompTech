import base64
import hashlib
import hmac
import secrets
import string
import struct
import time
import asyncio


def otp(key: str) -> str:
    key_bytes = base64.b32decode(key)
    counter = int(time.time() // 30)
    counter_bytes = struct.pack(">Q", counter)
    hmac_hash = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
    start = hmac_hash[-1] & 0xf
    code = struct.unpack(">I", hmac_hash[start:start+4])[0] & 0x7fffffff
    return str(code)[-6:].zfill(6)

def password(length: int = 8) -> str:
    if length < 8:
        raise ValueError("Password length must be at least 8 characters")
    
    digits = string.digits
    letters_up = string.ascii_uppercase
    letters_low = string.ascii_lowercase
    punctuation = string.punctuation
    
    password_symbols = digits + letters_up + letters_low + punctuation
    
    password = None
    
    async def make_password() -> str:
        password = "".join(secrets.choice(password_symbols) for _ in range(length))
        if not any(char in punctuation for char in password):
            return
        if not any(char in digits for char in password):
            return
        if not any(char in letters_up for char in password):
            return
        if not any(char in letters_low for char in password):
            return
        return password
    
    async def password_wrapper():
        runs = []
        for _ in range(10):
            runs.append(asyncio.create_task(make_password()))
        await asyncio.gather(*runs)
        return next((password.result() for password in runs if password.result() is not None), None)
    
    while True:
        password = asyncio.run(password_wrapper())
        
        if not password:
            continue
        return password
