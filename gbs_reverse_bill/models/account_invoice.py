# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


class AccountMove(models.Model):
    _inherit = "account.move"


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
