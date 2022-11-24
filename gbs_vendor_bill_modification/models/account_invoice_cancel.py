from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import UserError, ValidationError


class AccountInvoiceCancel(models.Model):
    _inherit = 'account.invoice'

    invoice_cancel_reason = fields.Char(string="Cance Reason")