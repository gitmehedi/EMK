from datetime import date, datetime
from dateutil import relativedelta
import json
import time


from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID, api
import logging

from openerp import api, fields, models
from openerp.osv import osv

import re


class InharitedStockInventoryLineExtend(models.Model):
    _inherit = 'stock.inventory.line'
    
    color_attribute_id = fields.Many2one('product.attribute', string='Color Attribute')
    color_value_id = fields.Many2one('product.attribute.value', string='Color')
    size_attribute_id = fields.Many2one('product.attribute', string='Size Attribute')
    size_value_id = fields.Many2one('product.attribute.value', string='Size')
    

class InheritedStockInventory(models.Model):
    _inherit = 'stock.inventory'
    
    product_tmp_id = fields.Many2one('product.template', string='Product')
    
    def prepare_inventory_matrix(self, cr, uid, ids, context=None):
        print ""
        inventory_line_obj = self.pool.get('stock.inventory.line')
        for inventory in self.browse(cr, uid, ids, context=context):
            # If there are inventory lines already (e.g. from import), respect those and set their theoretical qty
            line_ids = [line.id for line in inventory.line_ids]
            if not line_ids and inventory.filter == 'product':
                #compute the inventory lines and create them
                vals = self._get_inventory_matrix_lines(cr, uid, inventory, context=context)
                for product_line in vals:
                    if product_line['size_attribute_id'] and product_line['color_attribute_id']:
                        inventory_line_obj.create(cr, uid, product_line, context=context)
        return self.write(cr, uid, ids, {'state': 'confirm', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

    def _get_inventory_matrix_lines(self, cr, uid, inventory, context=None):
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        
        location_ids = location_obj.search(cr, uid, [('id', 'child_of', [inventory.location_id.id])], context=context)
        
        product_varient=self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', inventory.product_tmp_id.id)], context=context)
        
        vals = []
        
        for objproduct in product_varient:
            domain = ' location_id in %s'
            args = (tuple(location_ids),)
            domain += ' and product_id = %s'
            args += (objproduct,)
        
            cr.execute('''
               SELECT product_id, sum(qty) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
               FROM stock_quant WHERE''' + domain + '''
               GROUP BY product_id, location_id, lot_id, package_id, partner_id
            ''', args)
            
            
            print ""
            
            if cr.rowcount==0:
                product_line={}
                product_line['inventory_id'] = inventory.id
                product_line['theoretical_qty'] =0
                product_line['location_id']=inventory.location_id.id
                product_line['product_id']=objproduct
                product = product_obj.browse(cr, uid, objproduct, context=context)
                
                line_extend=self.pool.get('product.attribute.line.extend').search(cr, uid, [('product_id', '=', objproduct)], context=context)
                varient = self.pool.get('product.attribute.line.extend').browse(cr, uid, line_extend, context=context)
        
                product_line['color_attribute_id'] =varient.color_attribute_id.id 
                product_line['color_value_id'] = varient.color_value_id.id 
                product_line['size_attribute_id'] = varient.size_attribute_id.id 
                product_line['size_value_id'] = varient.size_value_id.id 
                
                product_line['product_uom_id'] = product.uom_id.id
                vals.append(product_line)
            else:
                for product_line in cr.dictfetchall():
                    #replace the None the dictionary by False, because falsy values are tested later on
                    for key, value in product_line.items():
                        if not value:
                            product_line[key] = False
                    product_line['inventory_id'] = inventory.id
                    product_line['theoretical_qty'] = product_line['product_qty']
        
                    if product_line['product_id']:
                        line_extend=self.pool.get('product.attribute.line.extend').search(cr, uid, [('product_id', '=', objproduct)], context=context)
                        varient = self.pool.get('product.attribute.line.extend').browse(cr, uid, line_extend, context=context)
                        product_line['color_attribute_id'] =varient.color_attribute_id.id 
                        product_line['color_value_id'] = varient.color_value_id.id 
                        product_line['size_attribute_id'] = varient.size_attribute_id.id 
                        product_line['size_value_id'] = varient.size_value_id.id 
                        product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
                        product_line['product_uom_id'] = product.uom_id.id
                    vals.append(product_line)
            domain=False
            args=False    
        return vals
