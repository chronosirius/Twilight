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

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img: 'PIL.Image.Image') -> 'PIL.Image.Image': #type: ignore
    """Crops max-size square from center"""
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def reorder_index(j: list[dict], indexid: str = 'index'):
    l: list[dict | None] = list()
    for _ in range(len(j)):
        l.append(None)
    for d in j:
        if type(d[indexid]) != str:
            l[d[indexid]] = d
        else:
            match d[indexid]:
                case 'top':
                    l.insert(0, d)
                case 'bottom':
                    l.append(d)
    for i, k in enumerate(l):
        if k is None:
            del l[i]
    def _check(k):
        if k[indexid] == 'top':
            return float('-inf')
        elif k[indexid] == 'bottom':
            return float('inf')
        else:
            return k[indexid]
    return sorted(j, key=_check)

def get_timestamp() -> int:
    return round(datetime.utcnow().timestamp())

def xor(o1, o2) -> bool:
    return bool(o1) != bool(o2)

def expose(dict_: dict, keeplist: list, negate: bool = False):
    d = dict()
    for k in dict_:
        if xor(k in keeplist, negate):
            d[k] = dict_[k]
    return d