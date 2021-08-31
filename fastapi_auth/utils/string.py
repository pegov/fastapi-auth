import hashlib
import os

from passlib.pwd import genword


def create_random_string(length: int = 256) -> str:
    return genword(length=length)


def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def create_random_state() -> str:
    return hashlib.sha256(os.urandom(1024)).hexdigest()
