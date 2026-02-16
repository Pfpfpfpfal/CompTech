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

    digest = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 1_000_000).zfill(6)


def _is_valid_password(value: str) -> bool:
    return (
        any(char.islower() for char in value)
        and any(char.isupper() for char in value)
        and any(char.isdigit() for char in value)
        and any(char in string.punctuation for char in value)
    )


async def _make_password_once(length: int, alphabet: str) -> str | None:
    value = "".join(secrets.choice(alphabet) for _ in range(length))
    if _is_valid_password(value):
        return value
    return None


async def _generate_password_batch(length: int, alphabet: str, batch_size: int = 10) -> str | None:
    tasks = [asyncio.create_task(_make_password_once(length, alphabet)) for _ in range(batch_size)]
    results = await asyncio.gather(*tasks)
    return next((item for item in results if item is not None), None)


def password(length: int = 8) -> str:
    if length < 8:
        raise ValueError("Password length must be at least 8 characters")

    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    while True:
        value = asyncio.run(_generate_password_batch(length, alphabet))
        if value is not None:
            return value
