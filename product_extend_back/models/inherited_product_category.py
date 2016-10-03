from openerp import api, fields, models
import re
import openerp.modules
import logging

class InheritedProductCategory(models.Model):
    _inherit = 'product.category'
    
    @api.model
    def _getColorAttributeId(self):
        return [('attribute_id', '=', self.env.ref('product_extend_back.product_attribute_color').id)]
    @api.model
    def _getSizeAttributeId(self):
        return [('attribute_id', '=', self.env.ref('product_extend_back.product_attribute_size').id)]
    
    color_ids = fields.Many2many('product.attribute.value', 
                                 relation='product_category_attribure_color_rel',
                                 column1='category_id',
                                 column2='color_id',
                                 string='Color',  
                                 domain=_getColorAttributeId)
    size_ids = fields.Many2many('product.attribute.value', 
                                relation='product_category_attribure_size_rel',
                                 column1='category_id',
                                 column2='size_id',
                                string='Size', domain=_getSizeAttributeId)
    
    
    @api.multi
    def write(self, vals):
        #TODO: process before updating resource
        res= super(InheritedProductCategory, self).write(vals)
        self.env.cr.execute("Select correct_product_matrix(" + str(self.id) + ");")      
        return res
    
    def init(self, cr):
        f = openerp.modules.get_module_resource('product_extend_back', 'sqlscript/CORRECT_PRODUCT_MATRIX.sql')
        if not f:
            m = "File not found: 'CORRECT_PRODUCT_MATRIX.sql' (provided by module 'product_extend_back')."
            raise IOError(m)
        base_sql_file = openerp.tools.misc.file_open(f)
        try:
            cr.execute(base_sql_file.read())
        finally:
            base_sql_file.close()
