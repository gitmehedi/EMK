from odoo import api, fields, models


class SalesCustomerCommissionLine(models.Model):
    _name = 'sales.customer.commission.line'
    _rec_name = 'partner_id'

    total_com_amount = fields.Float(string='Total Commission Amount', compute='_compute_commission_amount')

    """Relational Fields"""
    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_commission_id = fields.Many2one('sales.commission.generate', string='Partner', ondelete='cascade')
    invoice_line_ids = fields.One2many('sales.customer.commission.invoice.line', 'commission_line_id')

    @api.multi
    def _compute_commission_amount(self):
        for inv in self:
            inv.total_com_amount = sum([v.commission_amount for v in inv.invoice_line_ids])


class SalesCustomerCommissionInvoiceLine(models.Model):
    _name = 'sales.customer.commission.invoice.line'
    _rec_name = 'invoice_id'

    invoiced_amount = fields.Float(string='Invoiced Amount', readonly=True)
    commission_amount = fields.Float(string='Commission Amount',readonly=True)

    """Relational Fields"""
    invoice_id = fields.Many2one('account.invoice', string='Invoice Id',readonly=True)
    commission_line_id = fields.Many2one('sales.customer.commission.line', string='Commission', ondelete='cascade')
