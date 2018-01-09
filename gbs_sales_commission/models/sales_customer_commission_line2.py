from odoo import api, fields, models


class SalesCustomerCommissionLine(models.Model):
    _name= 'sales.customer.commission.line2'

    partner_id = fields.Many2one('res.partner',string='Customer')
    invoice_id = fields.Many2one('account.invoice', string='Invoice Ids')
    line2_ids = fields.Many2one('sales.customer.commission.line', string='Id2', ondelete='cascade')

