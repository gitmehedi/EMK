# -*- coding: utf-8 -*-

import random

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_asset = fields.Boolean(default=False)
