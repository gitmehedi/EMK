from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    vbg_batch_id = fields.Many2one('vendor.bill.generation')
