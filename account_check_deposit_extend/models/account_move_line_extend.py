from openerp import models, fields, api

class AccountMoveLineExtends(models.Model):
    _inherit = 'account.move.line'
    
    cheque_date = fields.Date(compute='get_computed_columns', store=False,string='Cheque Date')
    cheque_number = fields.Char(compute='get_computed_columns', store=False,string='Cheque Number')
    
    is_postedtobank=fields.Boolean(string='Is Posted To Bank?',default=False)
    is_depositedtobank=fields.Boolean(string='Is Deposited To Bank?',default=False)
    is_rejectedfrombank=fields.Boolean(string='Is Rejected From Bank?',default=False)
    
    def get_computed_columns(self):
        move_ids = self.env.context.get('move_id', []) or []
        cur_obj = self.env['account.voucher']
                                                         
        for record in cur_obj.search([('move_id', 'in', move_ids)]):
            self.cheque_date = record.cheque_date
            self.cheque_number = record.cheque_number
            
            print "==========" + self.cheque_date
            print "==========" + self.cheque_number
            

#         res =self.env['account.voucher'].search([('move_id', '=', self.move_id.id)])
#         self.cheque_date=res[0].cheque_date
#         self.cheque_number=res[0].cheque_number
        