from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from bzrlib import api_minimum_version


class ChequeEntry(models.Model):
    _name = 'account.postdated.cheque'
    
    # database fields
    partner_info = fields.Many2one('res.partner', ondelete='set null', string='Name of Customer', required=True, help='Please enter customer name.')
    cheque_received_date = fields.Date(string='Cheque Received Date', default=fields.Date.today(), help='Please enter cheque received date.')
    cheque_number = fields.Char(string='Cheque Number', size=50, required=True, help='Please enter cheque number.')
    cheque_amount = fields.Float(string='Amount', digits=(18,2), required=True, help='Please enter amount.')
    posting_date = fields.Date(string='Posting Date', required=True, help='Please enter cheque posting date.',)
    issuing_bank = fields.Many2one('res.bank', ondelete='set null', string='Name of Bank', required=True)
    bank_branch_name = fields.Char(string='Branch', size=100, help='Please enter branch name.')
    deposit_date = fields.Date(string='Cheque Deposit Date', help='Please enter cheque deposit date.')
    confirm_date = fields.Date(string='Cheque Confirm Date', help='Please enter cheque confirm date.')
    reject_date = fields.Date(string='Cheque Reject Date', help='Please enter cheque reject date.')
    account_number_id = fields.Many2one('res.partner.bank', ondelete='set null', string='Company Account')
    state = fields.Selection([
               ('draft','Draft'),
               ('deposit','Deposit'),
               ('confirm','Confirm'),
               ('reject','Reject'),
           ], default='draft', string='Status', index=True, readonly=True, copy=False, states={'draft':[('readonly', False)]})
    
    @api.one
    def deposit_cheque(self):
        self.write({'state': 'deposit'})
        
    @api.one
    def confirm_cheque(self):
        self.write({'state': 'confirm'})
        
    @api.one
    def reject_cheque(self):
        self.write({'state': 'reject'})