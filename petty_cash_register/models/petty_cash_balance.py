from openerp import models, fields
import datetime

class petty_cash_balance(models.Model):

    _name = 'petty.cash.balance'

    name = fields.Char(string='Name')
    branch_id = fields.Many2one('res.branch', string='Branch Name')
    opening_amount = fields.Float(digits=(20,3), string="Opening Amount")
    closing_amount = fields.Float(digits=(20,3), string="Closing Amount")
    date = fields.Date()