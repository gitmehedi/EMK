# -*- coding: utf-8 -*-

import random
import re
import string
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import fields, _
from odoo.exceptions import ValidationError

DATE_PFORMAT = "%d/%m/%Y"
DATE_MFORMAT = "%Y-%m-%d"
DATE_WOUTH = "%Y-%m-%d"
DATE_WITHH = "%Y-%m-%d HH:MM:SS"


class Utility:
    message = {
        'email': 'Please provide valid email',
    }

    @staticmethod
    def token(length=8):
        alphanumeric = string.ascii_letters + string.digits
        return ''.join(random.SystemRandom().choice(alphanumeric) for i in xrange(length))

    def now(self, **kwargs):
        dt = datetime.now() + timedelta(**kwargs)
        return fields.Datetime.to_string(dt)

    @staticmethod
    def random_token():
        # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))

    @staticmethod
    def check_email(val):
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', val.lower())
        if match == None:
            raise ValidationError(_('Please provide valid email'))

    @staticmethod
    def check_url(val):
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', val)
        if match == None:
            raise ValidationError(_('Please provide valid URL'))

    @staticmethod
    def date_format(val):
        if val:
            data = datetime.strptime(val, DATE_PFORMAT)
            date = data.strftime(DATE_MFORMAT)
            return date
        else:
            return None

    @staticmethod
    def float_to_time(value):
        if value >= 0.0:
            ivalue = int(value)
            return "%02d:%02d" % (ivalue, (value - ivalue) * 60)
        else:
            value = abs(value)
            ivalue = int(value)
            return "-%02d:%02d" % (ivalue, (value - ivalue) * 60)

    @staticmethod
    def valid_email(email):
        if not re.match('^[^\s@]+@[^\s@]+\.[^\s@]+$', email.rstrip()):
            return False
        return True

    @staticmethod
    def valid_mobile(phone):
        pattern = re.compile(r'^(880)([0-9]{10})$')
        if not pattern.match(phone):
            return False
        return True

    @staticmethod
    def next_date(date, duration, time='years', format='%Y-%m-%d'):
        if time == 'years':
            rel_date = datetime.strptime(date, format) + relativedelta(years=duration)
        elif time == 'days':
            rel_date = datetime.strptime(date, format) + relativedelta(days=duration)
        next_date = rel_date.strftime(format)
        return next_date

    @staticmethod
    def valid_number(number):
        pattern = re.compile('^[0-9]$')
        if not pattern.match(number):
            return False
        return True

    @staticmethod
    def date_format(date, with_time=False):
        if with_time:
            date = datetime.strftime(date, DATE_WITHH)
        else:
            date = datetime.strftime(date, DATE_WOUTH)
        return date


class Message:
    UNLINK_WARNING = "[Warning] Approves and Rejected record cannot be deleted."
    UNLINK_INT_WARNING = "The operation cannot be completed, probably due to the following:\n " \
                     "- deletion: you may be trying to delete a record while other records still reference it"
