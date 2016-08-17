from openerp import api, fields, models
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
import time

class petty_cash_disbursement(models.Model):
    
    _name = 'petty.cash.disbursement'
    
    branch_id = fields.Many2one("res.branch", string='Branch', required=True)
    date = fields.Datetime(string='Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    #date = fields.Date(string='Date', copy=False)
    unclaim_of_yesterday = fields.Float(string='Unclaim of Yesterday')
    unclaim_of_today = fields.Float(string='Unclaim of Today')
    total_disbursement = fields.Float(compute='_amount_all',string="Total", readonly=True, digits_compute=dp.get_precision('Account'),)
    line_ids = fields.One2many('petty.cash.disbursement.line', 'disbursement_id', string='Bisbursement Line', 
                               required=True)
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('submit', 'Submit'),
            ('approve', 'Approve'),
            ], 'Status', select=True, readonly=True, default='draft')
    
    
    _defaults = {      
        'branch_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).branch_id.id,
    }
    
    @api.depends('line_ids.amount')
    def _amount_all(self):
        """
        Compute the total amounts of the Petty Cash.
        """
        for pcd in self:
            total_disbursement = 0.0
            for line in pcd.line_ids:
                total_disbursement += line.amount
            pcd.update({
                'total_disbursement': total_disbursement,
            })
    
    @api.depends('line_ids')
    def action_submit(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not any(line.state != 'submit' for line in o.line_ids):
                raise osv.except_osv(_('Error!'),_('You cannot confirm a record which has no line.'))
            
        return self.write(cr, uid, ids, {'state':'submit'})
    
    def action_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'})
    
    @api.multi
    def name_get(self):
        res = {}
        for record in self:
            res[record.id] = record.branch_id.name + ' : ' + record.date
        return res
    
    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise Warning('You can only delete draft record!')
        return super(petty_cash_disbursement, self).unlink()
    
    
    
    