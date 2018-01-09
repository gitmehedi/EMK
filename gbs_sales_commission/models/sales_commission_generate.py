from odoo import api, fields, models
import datetime


class SalesCommissionGenerate(models.Model):
    _name = 'sales.commission.generate'
    _inherit = ['mail.thread']
    _rec_name = 'name'

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



            list1 = []
            list2 = []

            if account_invoice_pool:
                for acc_inv in account_invoice_pool:
                    vals = {}
                    vals['partner_id'] = acc_inv.partner_id.id
                    vals['invoiced_amount'] = acc_inv.amount_total
                    vals['amount_due'] = acc_inv.residual
                    vals['invoice_id'] = acc_inv.id
                    vals['commission_amount'] = acc_inv.generated_commission_amount
                    vals['sale_commission_id'] = comisn.id

                    list1.append(vals)

            for recs in list1:
                comisn.line_ids.create(recs)

            for lines in comisn.line_ids:
                vals2 = {}

                vals2['line2_ids'] = lines.id
                vals2['invoice_id'] = lines.invoice_id.id
                vals2['partner_id'] = lines.partner_id.id

                list2.append(vals2)

            for re in list2:
                comisn.env['sales.customer.commission.line2'].create(re)

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
