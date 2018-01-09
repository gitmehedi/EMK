from odoo import api, fields, models


class SalesCustomerCommissionLine(models.Model):
    _name= 'sales.customer.commission.line'

    partner_id = fields.Many2one('res.partner',string='Customer')
    invoiced_amount = fields.Float(string='Invoiced Amount')
    amount_due = fields.Float(string='Amount Due')
    invoice_id = fields.Many2one('account.invoice', string='Invoice Id')
    commission_amount = fields.Float(string='Commission Amount')


    """Relational Fields"""
    sale_commission_id = fields.Many2one('sales.commission.generate', string='Commission', ondelete='cascade')
    cust_coms_id2 = fields.One2many('sales.customer.commission.line2', 'line2_ids')

