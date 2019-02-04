from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
