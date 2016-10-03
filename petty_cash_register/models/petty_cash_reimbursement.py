from openerp import models, fields, api, exceptions
from openerp.osv import osv
import datetime


class petty_cash_reimbursement(models.Model):
    _name = 'petty.cash.reimbursement'

    name = fields.Char(string='Name')
    branch_id = fields.Many2one('res.branch', string='Branch Name', required=True)
    received_by = fields.Many2one('res.users', string='Received By', required=True)
    amount = fields.Float(digits=(20, 2), string="Amount", required=True)
    received_date = fields.Date('Receive Date', required=True)
    state = fields.Selection([('draft', 'Draft'), ('received', 'Received'), ],
                             'Status', select=True,
                             readonly=True,
                             default='draft')

    @api.multi
    def action_submit(self):
        pettycashbal_pool = self.env['petty.cash.balance']
        petty_balance = pettycashbal_pool.search(['&', ('branch_id','=',self.branch_id.id), 
                                                  ('date','=',self.received_date)])
        
        if petty_balance:
            ### Update Part
            in_amount = petty_balance.in_amount + self.amount
            cl_amount = petty_balance.closing_amount + self.amount
            petty_balance.write({'in_amount':in_amount,
                                 'closing_amount':cl_amount})
        else:
            #### Create Part
            ### First find out the closing balance of yesterday
            yesterday_balance = pettycashbal_pool.search(['&', ('branch_id','=',self.branch_id.id), 
                                                  ('date','<',self.received_date)])
            if not yesterday_balance:
                op_amount = 0
                
            if yesterday_balance:
                op_amount = yesterday_balance[0].closing_amount
                
            vals = {'branch_id':self.branch_id.id,
                    'date': self.received_date,
                    'opening_amount':op_amount,
                    'in_amount': self.amount,
                    'closing_amount':self.amount + op_amount}
            pettycashbal_pool.create(vals)
        return self.write({'state': 'received','received_by':self._uid})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'), _('You cannot delete! It is in %s state.') % (rec.state))
        return super(petty_cash_reimbursement, self).unlink()

