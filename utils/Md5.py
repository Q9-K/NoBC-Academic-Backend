import hashlib
from random import Random


def create_salt(length=4):
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    random = Random()
    for i in range(length):
        # 每次从chars中随机取一位
        salt += chars[random.randint(0, len_chars)]
    return salt


def create_md5(pwd, salt):
    md5_obj = hashlib.md5()
    md5_obj.update((pwd + salt).encode("utf-8"))
    return md5_obj.hexdigest()
