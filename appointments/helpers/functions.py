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
    # if not re.findall(r"\+?\b[\d]{5}-[\d]{3}-[\d]{3}\b", phone.rstrip()):if not re.compile("(0|88)?[7-9][0-9]{9}",phone.strip()):
    # 1) Begins with 0 or 880
    # 2) Then contains 1 or 8 or 9.
    # 3) Then contains 9 digits
    # Pattern = re.compile("(0|880)?[1|2][0-9]{9}")
    Pattern = re.compile(r'^\+?(0|880)?[1-2]\d{9,13}$')
    if not Pattern.match(phone):
        return False
    return True

