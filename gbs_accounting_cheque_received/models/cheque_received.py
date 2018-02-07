from odoo import models, fields, api
import datetime


class ChequeReceived(models.Model):
    _name = 'accounting.cheque.received'
    _rec_name = 'name'

    state = fields.Selection([
        ('draft','Cheque Entry'),
        ('received','Confirm'),
        ('deposited','Deposit to Bank'),
        ('honoured','Honoured'),
        ('dishonoured', 'Dishonoured'),
        ('returned', 'Returned to Customer'),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    name = fields.Char(string='Name',default='Testing')
    partner_id = fields.Many2one('res.partner', string="Customer", )
    bank_name = fields.Many2one('res.bank', string='Bank', )
    branch_name = fields.Char(string='Branch Name', required=True,default='Kawran Bazar')
    date_on_cheque = fields.Date('Date On Cheque', )
    cheque_amount = fields.Float(string='Amount', required=True,default='150')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order',)

    """ Methods """
    @api.multi
    def action_received(self):
        for cr in self:
            cr.state='received'

    @api.multi
    def action_deposited(self):
        for cr in self:
            cr.state='deposited'

    @api.multi
    def action_honoured(self):
        for cr in self:
            cr.state='honoured'

    @api.multi
    def action_dishonoured(self):
        for cr in self:
            cr.state='dishonoured'

    @api.multi
    def action_returned_to_customer(self):
        for cr in self:
            cr.state='returned'


