from datetime import datetime
from hashlib import new
from random import randint
from os import getpid, getppid

def generate_token() -> str:
    return hex((round(datetime.utcnow().timestamp()*1000) + randint(0, 9_999_999_999_999_999))*(getpid()*getppid() + randint(0, 999_999))).lstrip('0x').upper()

def quickhash(string: str) -> str:
    a = new('sha512')
    a.update(string.encode())
    return a.hexdigest()

def list_to_dict(arr: list, key: str = 'id') -> dict:
    proc: dict = dict()
    for t, o in enumerate(arr):
        proc[o[key]] = arr[t]
    return proc

def get_month_name_from_number(num):
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][num-1]

def datetime_to_dict(dt=None):
    if dt is None:
        dt = datetime.utcnow()

    return {
        'year': dt.year,
        'month': get_month_name_from_number(dt.month),
        'day': dt.day,
        'hour': dt.hour,
        'minute': dt.minute
    }