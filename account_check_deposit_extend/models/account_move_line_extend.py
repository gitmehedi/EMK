from openerp import models, fields, api

class AccountMoveLineExtends(models.Model):
    _inherit = 'account.move.line'
    
    cheque_date = fields.Date(compute='get_computed_columns', store=False,string='Cheque Date')
    cheque_number = fields.Char(compute='get_computed_columns', store=False,string='Cheque Number')
    
    is_postedtobank=fields.Boolean(string='Is Deposited To Bank?',default=False)
    
    def get_computed_columns(self):
        res =self.env['account.voucher'].search([('move_id', '=', self.move_id.id)])
        self.cheque_date=res[0].cheque_date
        self.cheque_number=res[0].cheque_number