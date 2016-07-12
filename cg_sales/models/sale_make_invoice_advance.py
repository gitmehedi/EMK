##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    
    def _check_warehouse(self, cr, uid, so, context=None):
        #print "_check_warehouse"
        locobj = self.pool.get('stock.location')
        stockpicking = self.pool.get('stock.picking')
        domain = ['|', ('state','=','assigned'), ('state','=','confirmed')]
        domain = ['&'] + domain + [('sale_id','=',so.id)]
        pick_ids = stockpicking.search(cr, uid, domain)

        for picking in stockpicking.browse(cr, uid, pick_ids, context):
            for line in picking.move_lines:
                result = locobj._product_get_report(cr, uid, [line.location_id.id], [line.product_id.id])
                if result.get('product',False):
                    if result['product'][0]['prod_qty']<line.product_uos_qty:
                        raise osv.except_osv('Warning!',('Stock is not available for this product: "%s"') % (line.product_id.name))
                        return False
                else:
                    raise osv.except_osv('Warning!',('Stock is not available for this product: "%s"') % (line.product_id.name))
                    return False
        return True
    
    def _check_credit_limit(self, cr, uid, so, context):
        #print "_check_credit_limit"
        if so:
            if ((so.amount_total + so.partner_id.credit)<so.partner_id.credit_limit):
                return True
            else:
                user = self.pool.get('res.users').browse(cr, uid, uid, context)
                grpobj = self.pool.get('res.groups')
                grp_ids = grpobj.search(cr, uid, [('name','=','Invoice Creator (Over Customer Credit Limit)')])
                grp = grpobj.browse(cr, uid, grp_ids[0])
                                
                if grp in user.groups_id:
                    return True
                
                raise osv.except_osv('Warning!',('To proceed please check the customer credit limit.'))
                return False
        return False
   
    def create_invoices(self, cr, uid, ids, context=None):
        """ create invoices for the active sales orders """
        #print "sale_advance_payment_inv:create_invoices"
        sale_obj = self.pool.get('sale.order')
        sale_ids = context.get('active_ids', [])
        so = sale_obj.browse(cr, uid, sale_ids[0])
        
        if so.so_type and so.so_type == 'normal':
            res = super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids, context)
            return res
        
        if so.so_type and so.so_type == 'invf':
            ### First Check the Warehouse If SKU is available
            if not self._check_warehouse(cr, uid, so, context):                
                return False
                    
            ### Then Check the credit limit
            if not self._check_credit_limit(cr, uid, so, context):
                return False
        
            res = super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids, context)
            return res
        
        return False

sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
