from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    so_type = fields.Char(string='Sale Order Type', compute='_compute_sale_order_type')

    @api.depends('sale_type_id')
    def _compute_sale_order_type(self):
        for rec in self:
            rec.so_type = rec.sale_type_id.sale_order_type
