# -*- coding: utf-8 -*-

import re
import random, string

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

DATE_PFORMAT = "%d/%m/%Y"
DATE_MFORMAT = "%Y-%m-%d"


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
