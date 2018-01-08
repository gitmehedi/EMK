from odoo import api, fields, models


class SalesCustomerCommissionLine(models.Model):
    _name= 'sales.customer.commission.line'

    customer_id = fields.Char(string='Customer')
    invoiced_amount = fields.Float(string='Invoiced Amount')
    amount_due = fields.Float(string='Amount Due')
    invoice_id = fields.Char(string='Invoice Id', size=50)
    commission_amount = fields.Float(string='Commission Amount')


    """Relational Fields"""
    sale_commission_id = fields.Many2one('sales.commission.generate', string='Commission', ondelete='cascade')

