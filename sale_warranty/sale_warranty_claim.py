from openerp.osv import fields, osv
import datetime
import time
from openerp.tools.translate import _

class sale_warranty_claim(osv.osv):
    
    _name = 'sale.warranty.claim'
    
    def _check_applicable(self, cr, uid, ids, field, arg, context=None):
        res = dict.fromkeys(ids, False)
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.expire_date >= claim.claim_date:
                res[claim.id] = True
            else:
                res[claim.id] = False
            
        return res
    
    _columns = {
          'name':fields.char('Claim No', size=64, required=True,
            readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True),
          'warranty_id':fields.many2one('sale.warranty', 'Warranty', required=True),
          'dealer_id':fields.related('warranty_id', 'dealer_id', type='many2one', relation='res.partner', string='Dealer', readonly=True),
          'customer_name':fields.related('warranty_id', 'customer_name', type='char', string='Customer', readonly=True),
          'claim_date': fields.date('Date of Claim', required=True),
          'expire_date': fields.related('warranty_id', 'expire_date', type="date", string='Expire Date', readonly=True),
          'applicable': fields.function(_check_applicable, type='boolean', string='Applicable', readonly=True),
          'replace_ids': fields.one2many('warranty.replace.product', 'claim_id', 'Replaced Products'),
          'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('receive', 'Received'),
            ('approve', 'Approved'),
            ('reject', 'Reject'),
            ('done', 'Done'),
        ], 'Status', select=True, readonly=True),
            }
    
    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'})
   
    def approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'})
    
    def done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context) 
    
    def receive(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'receive'}, context=context)
    
    def reject(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'reject'})
    
    _defaults = {
        'state': 'draft',
        'name': lambda obj, cr, uid, context: '/',
        'claim_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Claim No must be unique per Company!'),
    ]
    _order = 'name desc'
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.warranty.claim') or '/'
        return super(sale_warranty_claim, self).create(cr, uid, vals, context=context)
    
    # Delete record if it states in draft
    def unlink(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.state != 'draft':
                raise Warning(_('Cannot delete a claim that is not in draft state.'))
        return super(sale_warranty_claim, self).unlink(cr, uid, ids, context=context)
    
sale_warranty_claim()    