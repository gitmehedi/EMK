from odoo import api, fields, models
import datetime


class SalesCommissionGenerate(models.Model):
    _name = 'sales.commission.generate'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name')
    till_date = fields.Date(string='Till Date', required=True)

    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "Validate"),
        ('approved', "Approved"),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    """ Relational Fields"""
    line_ids = fields.One2many('sales.customer.commission.line', 'sale_commission_id')

    """ Related Methods """

    @api.multi
    def action_generate_sales_commission(self):
        for comisn in self:
            account_invoice_pool = comisn.env['account.invoice'].search(
                [('date_invoice', '<=', comisn.till_date), ('is_commission_generated', '=', False)])

            vals = {}
            if account_invoice_pool:
                for acc_inv in account_invoice_pool:
                    vals['customer_id'] = acc_inv.partner_id.name
                    vals['invoiced_amount'] = acc_inv.amount_total
                    vals['amount_due'] = acc_inv.residual
                    vals['invoice_id'] = acc_inv.number
                    vals['commission_amount'] = acc_inv.generated_commission_amount
                    vals['sale_commission_id'] = comisn.id

                    comisn.line_ids.create(vals)

            comisn.state = 'validate'

    @api.multi
    def action_approve_sales_commission(self):

        for inv in self:
            for inv_line in inv.line_ids:
                account_invoice_pool = inv.env['account.invoice'].search(
                    [('move_name', '=', inv_line.invoice_id)])

                for acc_inv in account_invoice_pool:
                    acc_inv.write({'is_commission_generated': True})

        inv.state = 'approved'