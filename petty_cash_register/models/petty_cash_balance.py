from openerp import models, fields
import datetime

class petty_cash_balance(models.Model):

    _name = 'petty.cash.balance'

    branch_id = fields.Many2one('res.branch', string='Branch Name', required=True)
    opening_amount = fields.Float(digits=(20,2), string="Opening Amount", default=0.0)
    closing_amount = fields.Float(digits=(20,2), string="Closing Amount", default=0.0)
    in_amount = fields.Float(digits=(20,2), string="Closing Amount", default=0.0)
    out_amount = fields.Float(digits=(20,2), string="Closing Amount", default=0.0)
    date = fields.Date()
    
    _order = 'id desc' 