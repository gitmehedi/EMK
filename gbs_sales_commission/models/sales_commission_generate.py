import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError


class SalesCommissionGenerate(models.Model):
    _name = 'sales.commission.generate'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    till_date = fields.Date(string='Till Date', required=True)

    state = fields.Selection([
        ('draft', "To Submit"),
        ('approved', "Approved"),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    """ Relational Fields"""
    line_ids = fields.One2many('sales.customer.commission.line', 'sale_commission_id', string='Invoices')

    """ Related Methods """

    @api.multi
    def action_generate_sales_commission(self):
        vals = {}
        for comm in self:
            invoices = comm.env['account.invoice'].search(
                [('date_invoice', '<=', comm.till_date), ('is_commission_generated', '=', False)])

            rec = {record.partner_id.id: [] for record in invoices}

            for vals in invoices:
                val = {}
                val['invoiced_amount'] = vals.amount_total
                val['commission_amount'] = vals.generated_commission_amount
                val['invoice_id'] = vals.id
                rec[vals.partner_id.id].append(val)

            for record in rec:
                res = comm.line_ids.create({'partner_id': record, 'sale_commission_id': comm.id})
                for list in rec[record]:
                    value = {}
                    value['invoiced_amount'] = list['invoiced_amount']
                    value['commission_amount'] = list['commission_amount']
                    value['invoice_id'] = list['invoice_id']
                    value['commission_line_id'] = res.id

                    res.invoice_line_ids.create(value)

    @api.multi
    def action_approve_sales_commission(self):
        for inv in self:
            for inv_line in inv.line_ids:
                for cust_invoice in inv_line.invoice_line_ids:
                    account_invoice_pool = inv.env['account.invoice'].search([('id', '=', cust_invoice.invoice_id.id)])
                    if not account_invoice_pool.is_commission_generated:
                        account_invoice_pool.write({'is_commission_generated': True})
                    else:
                        raise UserError("Commission line is already approved. Please delete customer '%s' from line and then Generate again." %(account_invoice_pool.partner_id.name))


        inv.state = 'approved'
