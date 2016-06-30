from openerp.osv import fields, osv
import time
from openerp.tools.translate import _

class customer_creditlimit_assign(osv.osv):
    
    _name = 'customer.creditlimit.assign'
    
    _description = "Credit limit assign"
    
    _columns = {
          'name':fields.char('Name', required=True, states={'approve': [('readonly', True)]}),
          'approve_date': fields.datetime('Approve Date', readonly=True),
          'credit_limit':fields.float('Limit', states={'approve': [('readonly', True)]}),
          'limit_ids': fields.one2many('res.partner.limits', 'assign_id', 'Limits', readonly=True),
          'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
        ], 'Status', select=True, readonly=True),
                }
    
    _defaults = {
        'state': 'draft',
    }
    
    def draft_creditlimit_run(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    
    def approve_creditlimit_run(self, cr, uid, ids, context=None):
        limit_pool = self.pool.get('res.partner.limits')
        partner_pool = self.pool.get('res.partner')
        for assign in self.browse(cr, uid, ids, context):
            for limit in assign.limit_ids:
                limit_pool.write(cr, uid, [limit.id], {'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')}, context)
                partner_pool.write(cr, uid, [limit.partner_id.id], {'credit_limit':limit.value}, context=context)
        return self.write(cr, uid, ids, {'state': 'approve', 'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        for limit in self.browse(cr, uid, ids, context=context):
            if limit.state in ['approve']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a record which is not draft state!'))
        return super(customer_creditlimit_assign, self).unlink(cr, uid, ids, context)
    
customer_creditlimit_assign()


class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    
    def _current_limit(self, cr, uid, ids, assign_date, arg, context=None):
        return self._get_current_limit(cr, uid, ids, raise_on_no_limit=False, context=context)
    
    def _get_current_limit(self, cr, uid, ids, raise_on_no_limit=True, context=None):
        if context is None:
            context = {}
        res = {}

        date = context.get('date') or time.strftime('%Y-%m-%d')
        for id in ids:
            cr.execute('SELECT value FROM res_partner_limits '
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
                raise osv.except_osv(_('Error!'),_("No credit value associated for credit '%s' for the given period" % (credit.lc_date)))
        return res
    
    _columns = {
          'limit_ids': fields.one2many('res.partner.limits', 'partner_id', "Limits", domain=[('state','=','approve')],),
          'credit_limit': fields.function(_current_limit, string='Credit Limit', type = 'float', store=True),
        }

class res_partner_limits(osv.osv):
    
    _name = 'res.partner.limits'
    
    _columns = {
          'partner_id': fields.many2one('res.partner', "Customer",),
          'assign_date': fields.date("Date", readonly=True),
          'value':fields.float('Limit'),
          'assign_id': fields.many2one('customer.creditlimit.assign', "Batch",),
          'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
        ], 'Status', select=True, readonly=True),
                
        }
    
    def unlink(self, cr, uid, ids, context=None):
        for limit in self.browse(cr, uid, ids, context=context):
            if limit.state in ['approve']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a value which is not draft state!'))
        return super(res_partner_limits, self).unlink(cr, uid, ids, context)
    
    _defaults = {
        'assign_date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'approve',
    }
    
    _order = "assign_date desc, id desc"
    
res_partner_limits()
