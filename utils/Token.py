from django.conf import settings
import jwt


def generate_token(dict, outdate_time):
    dict['exp'] = outdate_time
    value = jwt.encode(dict=dict, key=settings.JWT_KEY)
    return value.decode()


def get_value(token):
    try:
        value = jwt.decode(token, key=settings.JWT_KEY)
    except Exception as e:
        return None
    return value
