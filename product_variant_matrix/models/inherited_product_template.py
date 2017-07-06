
from openerp import api, fields, models
import re

class InheritedProductAttributeLineExtend(models.Model):
    _name = 'product.attribute.line.extend'
    
    product_tmp_id = fields.Many2one('product.template', string='Label', required=False,ondelete='cascade')
    
    color_attribute_id = fields.Many2one('product.attribute', string='Color Attribute',required=True)
    color_value_id = fields.Many2one('product.attribute.value', string='Color',required=True)
    size_attribute_id = fields.Many2one('product.attribute', string='Size Attribute',required=True)
    size_value_id = fields.Many2one('product.attribute.value', string='Size',required=True)
    
    product_id = fields.Many2one('product.product', string='Product')
    
    #stock = fields.Float('Label', digits=(16, 2))
    is_active = fields.Boolean('Active')
    

    
class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    product_variant_check = fields.Boolean('Show Variant Matrix', default=True)
    attribute_line_extend_ids = fields.One2many('product.attribute.line.extend', 'product_tmp_id', string='')
    
    def update_product_variant(self, product_tmp_id):



        attribute_line_extend_ids=self.env['product.attribute.line.extend'].search([('product_tmp_id', '=', product_tmp_id)],order='id asc')

        #Get Product Variant List
        product_varient=self.env['product.product'].search(['|','&',('product_tmpl_id', '=', product_tmp_id),('active', '=', True),('active', '=', False)],order='id asc')
        """
            System Will update manipulate data.
            * Active/Inactive product variant
            * set product id into the attribute_line_extend
        """
        for attribute_line_extend in attribute_line_extend_ids:
            for product in product_varient:
                color_Value_found=False
                size_Value_found=False
                for att_vale in product.attribute_value_ids:
                    if (att_vale.attribute_id.id==attribute_line_extend.color_attribute_id.id 
                        and att_vale.id==attribute_line_extend.color_value_id.id):
                        color_Value_found=True
                        
                    elif (att_vale.attribute_id.id==attribute_line_extend.size_attribute_id.id 
                        and att_vale.id==attribute_line_extend.size_value_id.id):
                        size_Value_found=True
                        
                if (size_Value_found==True and color_Value_found==True):
                    product.write({'active': attribute_line_extend.is_active})
                    attribute_line_extend.write({'product_id':product.id}) 
                    


    @api.model
    def create(self, vals):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(InheritedProductTemplate, self).create(vals)

        for att in product_template_id.attribute_line_ids:
            if att.attribute_id.name == 'Color':
                color_ids = att.value_ids
            if att.attribute_id.name == 'Size':
                size_ids = att.value_ids
            print att

        if (len(color_ids) > 0 and len(size_ids) > 0):
            #product_template_id.attribute_line_ids = []
            product_template_id.attribute_line_extend_ids = []

            # Add Color#
            # product_attribute_line_obj = self.attribute_line_ids.new()
            # product_attribute_line_obj.attribute_id = color_ids[0].attribute_id.id
            # for color in color_ids:
            #     product_attribute_value_obj = product_attribute_line_obj.value_ids.new()
            #     product_attribute_value_obj = color
            #     product_attribute_line_obj.value_ids = product_attribute_line_obj.value_ids | product_attribute_value_obj
            #
            # self.attribute_line_ids = self.attribute_line_ids | product_attribute_line_obj

            # Add Size#
            # product_attribute_line_obj = self.attribute_line_ids.new()
            # product_attribute_line_obj.attribute_id = size_ids[0].attribute_id.id
            # for size in size_ids:
            #     product_attribute_value_obj = product_attribute_line_obj.value_ids.new()
            #     product_attribute_value_obj = size
            #     product_attribute_line_obj.value_ids = product_attribute_line_obj.value_ids | product_attribute_value_obj
            #
            # self.attribute_line_ids = self.attribute_line_ids | product_attribute_line_obj

            # Matrix Row Populate
            for color in color_ids:
                for size in size_ids:
                    attribute_line_extend_obj = self.attribute_line_extend_ids.new()
                    attribute_line_extend_obj.color_attribute_id = color.attribute_id
                    attribute_line_extend_obj.color_value_id = color

                    attribute_line_extend_obj.size_attribute_id = size.attribute_id
                    attribute_line_extend_obj.size_value_id = size
                    attribute_line_extend_obj.is_active = True
                    product_template_id.attribute_line_extend_ids = product_template_id.attribute_line_extend_ids | attribute_line_extend_obj

        self.update_product_variant(product_template_id.id)

        return product_template_id
    
    @api.multi
    def write(self,vals):
        #TODO: process before updating resource
        res = super(InheritedProductTemplate, self).write(vals)
        self.update_product_variant(self.id)
        return res 
    
    @api.onchange('categ_id')
    def onchange_category(self):
        
        product_category=self.env['product.category'].search([('id', '=', self.categ_id.id)])

        if(len(product_category.color_ids)>0 and len(product_category.size_ids)>0):
            self.attribute_line_ids=[]
            self.attribute_line_extend_ids=[]
            
            #Add Color#
            product_attribute_line_obj=self.attribute_line_ids.new()
            product_attribute_line_obj.attribute_id=product_category.color_ids[0].attribute_id.id
            for color_ids in product_category.color_ids:
                product_attribute_value_obj=product_attribute_line_obj.value_ids.new()
                product_attribute_value_obj=color_ids
                product_attribute_line_obj.value_ids=product_attribute_line_obj.value_ids|product_attribute_value_obj
            
            self.attribute_line_ids = self.attribute_line_ids | product_attribute_line_obj
        
            #Add Size#
            product_attribute_line_obj=self.attribute_line_ids.new()
            product_attribute_line_obj.attribute_id=product_category.size_ids[0].attribute_id.id
            for size_ids in product_category.size_ids:
                product_attribute_value_obj=product_attribute_line_obj.value_ids.new()
                product_attribute_value_obj=size_ids
                product_attribute_line_obj.value_ids=product_attribute_line_obj.value_ids|product_attribute_value_obj
            
            self.attribute_line_ids = self.attribute_line_ids | product_attribute_line_obj
            
            #Matrix Row Populate
            for color_ids in product_category.color_ids:
               for size_ids in product_category.size_ids:
                   attribute_line_extend_obj=self.attribute_line_extend_ids.new()
                   attribute_line_extend_obj.color_attribute_id = color_ids.attribute_id
                   attribute_line_extend_obj.color_value_id =color_ids
                    
                   attribute_line_extend_obj.size_attribute_id = size_ids.attribute_id
                   attribute_line_extend_obj.size_value_id = size_ids
                   attribute_line_extend_obj.is_active = True
                   self.attribute_line_extend_ids = self.attribute_line_extend_ids | attribute_line_extend_obj
            