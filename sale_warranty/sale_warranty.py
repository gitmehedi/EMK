from openerp.osv import fields, osv
import datetime
import time
import logging
import traceback
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class sale_warranty(osv.osv):
    
    _name = 'sale.warranty'
    
    _columns = {
          'name':fields.char('Warranty No', size=64, required=True,
            readonly=True, states={'draft': [('readonly', False)]}, select=True),
          'serial_no':fields.char('Serial No', required=True),
          'sale_date':fields.date('Date of Sale', required=True),
          'expire_date':fields.date('Expire Date', readonly=True),
          'dealer_id':fields.many2one('res.partner', 'Dealer', required=True),
          'user_id': fields.many2one('res.users', 'Users', required=True),
          'product_id':fields.many2one('product.product', 'Product', required=True),
          'product_tmp_id': fields.related('product_id', 'product_tmpl_id', relation="product.template",
                                           type="many2one", string="Product" ),
          'product_type': fields.related('product_tmp_id', 'categ_id', relation="product.category",
                                     type="many2one", string="Product Category", readonly=True),
          'claim_ids': fields.one2many('sale.warranty.claim', 'warranty_id', 'Claim'),
          'replace_ids': fields.one2many('warranty.replace.product', 'warranty_id', 'Replaced Products'), 
          'customer_name':fields.char('Customer Name', required=True),
          'customer_address':fields.char('Customer Address', required=True),
          'customer_mobile':fields.char('Customer Mobile', required=True),
          'customer_tel':fields.char('Customer Telephone', required=True),
          'batch_no':fields.char('Batch No', required=True),
          'model':fields.char('Model'),
          'meter':fields.integer('Meter'),
          'registration':fields.char('Registration'),
          'invoiced':fields.boolean('Invoiced'),
          'application_type': fields.selection([
            ('mvehicle', 'Vehicle'),
            ('bdvehicle', 'Battery Driven Vehicle'),            
            ('ups', 'UPS'),
            ('hups', 'Home UPS'),
            ('oups', 'Online UPS'),
            ('ship', 'Ship'),
            ('boat', 'Boat'),
            ('generator', 'Generator'),
            ('others', 'Others'),
        ], 'Application Type', select=True, required=True),
          'fuel': fields.selection([
            ('Octen', 'Octen'),
            ('Petrol', 'Petrol'),
            ('Diesel', 'Diesel'),
            ('CNG', 'CNG'),
        ], 'Fuel Type', select=True),
          'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('reject', 'Reject'),
        ], 'Status', select=True, readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
        'name': lambda obj, cr, uid, context: '/',
        'user_id': lambda self,cr,uid,ctx: uid,
        'sale_date': lambda *a: time.strftime('%Y-%m-%d'),
        'application_type': 'mvehicle',
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Warranty No must be unique per Company!'),
    ]
    _order = 'name desc'
    
    def onchange_product(self, cr, uid, ids, product_id,context=None):
        print "------72-------onchange_product----------------------------------------"
        #result = {'value': {'product_type': False}}
        result = {'value':{}}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id,context=context)
            result['value'] = {'product_type': product.product_tmpl_id.categ_id.id}
        print result
        return result
    
    def sale_confirm(self, cr, uid, ids, context=None):
        print "----------------------sale_confirm-----------------------------"        
        vals = {'state': 'confirm'}        
        warranty = self.browse(cr, uid, ids[0], context)
        if warranty:
            warranty_period = 0
            if warranty.product_id.warranty > 0.0:
                warranty_period = warranty.product_id.warranty
            elif warranty.product_id.categ_id.warranty_period > 0.0:
                warranty_period = warranty.product_id.categ_id.warranty_period
            else:
                #Send Warraning that this product is not under warranty coverage
                warning_msgs = "'%s' is not under warranty coverage" % (warranty.product_id.name)                
                raise osv.except_osv('Warning!', warning_msgs)
                return False
            
            sale_date = datetime.datetime.strptime(warranty.sale_date,'%Y-%m-%d')
            date1 = sale_date + relativedelta(months=int(warranty_period))
            date2 = date1 - relativedelta(days=1)
            expire_date = datetime.datetime.strptime(date2.isoformat(),'%Y-%m-%dT%H:%M:%S').date()
            vals = {'expire_date':expire_date,'state': 'confirm'}            
                
        return self.write(cr, uid, ids, vals, context)
   
    def sale_approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'})
    
    def sale_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context) 
   
    def sale_refuse(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'reject'})
    
    def create_claim(self, cr, uid, ids, context=None):
        claim_obj = self.pool.get('sale.warranty.claim')

        claim_values = {
                    'warranty_id': ids[0],
        }

        claim_id = claim_obj.create(cr, uid, claim_values, context=context)
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.warranty.claim',
            'res_id': claim_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
    
    def unlink(self, cr, uid, ids, context=None):
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.state in ['confirm', 'reject']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a record which is not draft state!'))
        return super(sale_warranty, self).unlink(cr, uid, ids, context)
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.warranty') or '/'
        return super(sale_warranty, self).create(cr, uid, vals, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.warranty') or '/',
            'expire_date': False,
        })
        return super(sale_warranty, self).copy(cr, uid, id, default, context=context)
    
    
sale_warranty()