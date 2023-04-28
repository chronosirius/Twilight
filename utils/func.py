from datetime import datetime as dt
from hashlib import new
from random import randint
from os import getpid, getppid

def generate_token() -> str:
    return hex((round(dt.utcnow().timestamp()*1000) + randint(0, 9_999_999_999_999_999))*(getpid()*getppid() + randint(0, 999_999))).lstrip('0x').upper().zfill(20)[0:20]

def quickhash(string: str) -> str:
    a = new('sha512')
    a.update(string.encode())
    return a.hexdigest()

def list_to_dict(arr: list, key: str = 'id') -> dict:
    proc: dict = dict()
    for t, o in enumerate(arr):
        proc[o[key]] = arr[t]
    return proc

