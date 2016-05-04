# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
 
class AccountVoucherExtend(models.Model):
    
    _inherit = 'account.voucher'
    
    cheque_date = fields.Date(string='Cheque Date', default=fields.Date.today(), help='Please enter cheque date.')        
    cheque_number = fields.Char(string='Cheque Number', size=50,  help='Please enter cheque number.')
    issuing_bank = fields.Many2one('res.bank', ondelete='set null', string='Name of Bank', help='Please enter bank name.') 
    bank_branch_name = fields.Char(string='Branch Name', size=100, help='Please enter branch name.')