# -*- coding: utf-8 -*-
import re


def float_to_time(value):
    if value >= 0.0:
        ivalue = int(value)
        return "%02d:%02d" % (ivalue, (value - ivalue) * 60)
    else:
        value = abs(value)
        ivalue = int(value)
        return "-%02d:%02d" % (ivalue, (value - ivalue) * 60)


def valid_email(email):
    if not re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email.rstrip()):
        return False
    return True

def valid_mobile(phone):
    pattern = re.compile(r'^\+?(0|880)?[0-9]{9,13}$')
    if not pattern.match(phone):
        return False
    return True

