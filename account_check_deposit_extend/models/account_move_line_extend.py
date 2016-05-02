from openerp import models, fields, api

class AccountMoveLineExtends(models.Model):
    _inherit = 'account.move.line'
    
    #Database fields
    cheque_received_date = fields.Date(string='Cheque Received Date', default=fields.Date.today(), help='Please enter cheque received date.')
    cheque_number = fields.Char(string='Cheque Number', size=50,  help='Please enter cheque number.')
    posting_date = fields.Date(string='Cheque Posting Date', default=fields.Date.today(), help='Please enter cheque posting date.')
    issuing_bank = fields.Many2one('res.bank', ondelete='set null', string='Name of Bank') 
    bank_branch_name = fields.Char(string='Branch Name', size=100, help='Please enter branch name.')