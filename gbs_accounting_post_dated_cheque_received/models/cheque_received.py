from odoo import models, fields, api
import datetime


class ChequeReceived(models.Model):
    _name = 'accounting.cheque.received'
    #_inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    bank_name = fields.Many2one('res.partner.bank', string='Bank', required=True)
    branch_name = fields.Char(string='Branch Name', required=True)
    date_on_cheque = fields.Date('Date On Cheque', required=True)
    cheque_amount = fields.Float(string='Amount', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Ref.')

    state = fields.Selection([
        ('draft', "Draft"),
        ('approve', "Approved")
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')


    @api.multi
    def action_approve(self):
        for s in self:
            s.state = 'approve'