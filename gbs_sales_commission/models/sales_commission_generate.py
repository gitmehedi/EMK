import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError


class SalesCommissionGenerate(models.Model):
    _name = 'sales.commission.generate'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = 'Generate Commission'
    _order = 'id DESC'

    name = fields.Char(string='Name', required=True)
    till_date = fields.Date(string='Till Date', required=True)

    state = fields.Selection([
        ('draft', "To Submit"),
        ('approved', "Approved"),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    """ Relational Fields"""
    line_ids = fields.One2many('sales.customer.commission.line', 'sale_commission_id', string='Invoices',readonly=True)

    """ Related Methods """

    @api.multi
    def action_generate_sales_commission(self):
        for comm in self:
            if self.line_ids:
                self.line_ids.unlink()


            invoices = comm.env['account.invoice'].search(
                [('date_invoice', '<=', comm.till_date), ('is_commission_generated', '=', False)])

            rec = {record.partner_id.id: [] for record in invoices}

            for vals in invoices:
                for invoice_line in vals.invoice_line_ids:


                    if invoice_line.product_id in rec[vals.partner_id.id]:
                        rec[vals.partner_id.id]['invoiced_amount'] = rec[vals.partner_id.id][
                                                                         'invoiced_amount'] + invoice_line.invoice_id.amount_total
                    else:
                        val = {}
                        val['commission_amount'] = invoice_line.commission_amount
                        val['invoice_line_id'] = invoice_line.id
                        val['invoice_id'] = invoice_line.invoice_id.id
                        val['product_id'] = invoice_line.product_id.id
                        val['invoiced_amount'] = invoice_line.invoice_id.amount_total
                        rec[vals.partner_id.id].append(val)

            for record in rec:
                res = comm.line_ids.create({'partner_id': record, 'sale_commission_id': comm.id})
                for list in rec[record]:
                    value = {}
                    value['invoiced_amount'] = list['invoiced_amount']
                    value['commission_amount'] = list['commission_amount']
                    value['invoice_id'] = list['invoice_id']
                    value['invoice_line_id'] = list['invoice_line_id']
                    value['product_id'] = list['product_id']
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
                        raise UserError(
                            "Commission line is already approved. Please delete customer '%s' from line and then Generate again." % (
                            account_invoice_pool.partner_id.name))

        inv.state = 'approved'
