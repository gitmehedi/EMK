from openerp import models, fields,_
from openerp import api
import time
from openerp.tools.translate import _

class customer_creditlimit_assign(models.Model):
    
    _name = 'customer.creditlimit.assign'
    
    _description = "Credit limit assign"

    name = fields.Char('Name', required=True, states={'approve': [('readonly', True)]})
    approve_date = fields.Datetime('Approve Date')
    credit_limit = fields.Float('Limit', states={'approve': [('readonly', True)]})
    limit_ids = fields.One2many('res.partner.credit.limit', 'assign_id', 'Limits')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ],select=True, readonly=True,default='draft')

    @api.multi
    def approve_creditlimit_run(self, cr, uid, ids, context=None):
        limit_pool = self.pool.get('res.partner.credit.limit')
        partner_pool = self.pool.get('res.partner')
        for assign in self.browse(cr, uid, ids, context):
            for limit in assign.limit_ids:
                limit_pool.write(cr, uid, [limit.id], {'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')}, context)
                partner_pool.write(cr, uid, [limit.partner_id.id], {'credit_limit':limit.value}, context=context)
        return self.write(cr, uid, ids, {'state': 'approve', 'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        for limit in self.browse(cr, uid, ids, context=context):
            if limit.state in ['approve']:
                raise models.except_models(_('Warning!'),_('You cannot delete a record which is not draft state!'))
        return super(customer_creditlimit_assign, self).unlink(cr, uid, ids, context)
    
customer_creditlimit_assign()


class res_partner(models.Model):
    
    _inherit = 'res.partner'

    limit_ids = fields.One2many('res.partner.credit.limit', 'partner_id', "Limits",
                                domain=[('state', '=', 'draft')], ),
    credit_limit = fields.Float(compute='_current_limit', string='Credit Limit', store=True)
    
    def _current_limit(self, cr, uid, ids, assign_date, arg, context=None):
        return self._get_current_limit(cr, uid, ids, raise_on_no_limit=False, context=context)
    
    def _get_current_limit(self, cr, uid, ids, raise_on_no_limit=True, context=None):
        if context is None:
            context = {}
        res = {}

        date = context.get('date') or time.strftime('%Y-%m-%d')
        for id in ids:
            cr.execute('SELECT value FROM res_partner_credit_limit '
                       'WHERE partner_id = %s '
                       'AND assign_date <= %s '
                       'AND state = %s '
                       'ORDER BY assign_date desc, id desc LIMIT 1',
                       (id, date, "approve"))
            if cr.rowcount:
                res[id] = cr.fetchone()[0]
            elif not raise_on_no_limit:
                res[id] = 0
            else:
                credit = self.browse(cr, uid, id, context=context)
                raise models.except_models(_('Error!'),_("No credit value associated for credit '%s' for the given period" % (credit.lc_date)))
        return res
    



class res_partner_credit_limit(models.Model):
    
    _name = 'res.partner.credit.limit'
    _order = "assign_date desc, id desc"

    partner_id = fields.Many2one('res.partner', "Customer")
    assign_date = fields.Date("Date", readonly=True)
    value = fields.Float('Limit')
    assign_id = fields.Many2one('customer.creditlimit.assign', "Batch")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ],select=True, readonly=True, default='approve')

    
    def unlink(self, cr, uid, ids, context=None):
        for limit in self.browse(cr, uid, ids, context=context):
            if limit.state in ['approve']:
                raise models.except_models(_('Warning!'),_('You cannot delete a value which is not draft state!'))
        return super(res_partner_credit_limit, self).unlink(cr, uid, ids, context)
    
    _defaults = {
        'assign_date': lambda *a: time.strftime('%Y-%m-%d')
    }
    

    
res_partner_credit_limit()
