from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from bzrlib import api_minimum_version


class ChequeEntry(models.Model):
    _name = 'account.postdated.cheque'
    
    # database fields
    
    partner_info = fields.Many2one('res.partner', ondelete='set null', string='Name of Customer', required=True, help='Please enter customer name.')
    cheque_number = fields.Char(string='Cheque Number', size=50, required=True, help='Please enter cheque number.')
    cheque_received_date = fields.Date(string='Cheque Received Date', default=fields.Date.today(), help='Please enter cheque received date.')
    cheque_amount = fields.Float(string='Amount', digits=(18,2), required=True, help='Please enter amount.')
    posting_date = fields.Date(string='Posting Date', required=True, help='Please enter cheque posting date.',)
    issuing_bank = fields.Many2one('account.postdated.bank', ondelete='set null', string='Name of Bank', required=True)
    bank_branch_name = fields.Char(string='Branch', size=100, help='Please enter branch name.')
    deposit_date = fields.Date(string='Cheque Deposit Date', help='Please enter cheque deposit date.')
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
    
#     @api.one
#     def action_draft(self):
#         self.write({'state': 'draft'})
    
#     @api.one
#     def action_deposit(self):
#         self.write({'state': 'deposit'})
        
    @api.one
    def action_confirm(self):
        self.write({'state': 'confirm'})
        
    @api.one
    def action_reject(self):
        self.write({'state': 'reject'})