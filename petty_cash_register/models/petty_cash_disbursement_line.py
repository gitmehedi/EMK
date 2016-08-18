from openerp import models, fields
import datetime

class petty_cash_disbursement_line(models.Model):
    
    _name = 'petty.cash.disbursement.line'

   
    name = fields.Char(string=' Voucher #')
    disbursement_id = fields.Many2one("petty.cash.disbursement", string='Bisbursement', 
                                      required=True, ondelete='cascade',)
    account_id = fields.Many2one("account.account", string='Account', required=True)
    employee = fields.Char(string=' Employee')
    paid_to = fields.Char(string='Paid To')
    description = fields.Char(string='Description')
    amount = fields.Float(string='Amount')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('submit', 'Submit'),
            ('approve', 'Approve'),
            ], 'Status', readonly=True, copy=False, default='draft')
    
    _defaults = {
        'state': 'draft',
    }
    
    def button_submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'submit'})
