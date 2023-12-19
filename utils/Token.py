import time

from django.conf import settings
import jwt


def generate_token(dict, outdate_time):
    dict['exp'] = outdate_time + time.time()
    value = jwt.encode(dict, key=settings.JWT_KEY, algorithm='HS256')
    return value


def get_value(token):
    try:
        value = jwt.decode(token, key=settings.JWT_KEY, algorithms='HS256')
    except Exception as e:
        return None
    return value
