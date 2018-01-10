from odoo import api, fields, models


class SalesCustomerCommissionLine(models.Model):
    _name = 'sales.customer.commission.line'

    total_com_amount = fields.Float(string='Total Commission Amount')

    """Relational Fields"""
    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_commission_id = fields.Many2one('sales.commission.generate', string='Commission', ondelete='cascade')
    invoice_line_ids = fields.One2many('sales.customer.commission.invoice.line', 'commission_line_id')


class SalesCustomerCommissionInvoiceLine(models.Model):
    _name = 'sales.customer.commission.invoice.line'

    invoiced_amount = fields.Float(string='Invoiced Amount')
    commission_amount = fields.Float(string='Commission Amount')

    """Relational Fields"""
    invoice_id = fields.Many2one('account.invoice', string='Invoice Id')
    commission_line_id = fields.Many2one('sales.customer.commission.line', string='Commission', ondelete='cascade')
