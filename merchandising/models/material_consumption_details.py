from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class MaterialConsumptionDetails(models.Model):
    """
    Material Consumption Details
    """
    _name = 'material.consumption.details'
    
    # Required and Optional Fields
    quantity = fields.Float(string="Quantity", digits=(10, 2), default=1.00, required=True)
    wastage = fields.Float(string='Wastage %', digits=(2, 2), default=1.00, required=True)
    status = fields.Char(size=30, readonly=True)
    uom_category = fields.Integer(invisible=True)
    finish_goods = fields.Boolean(string='As Finish Goods Color', default=False)
    
    # Model Relationship
    size_qty_ids = fields.One2many('material.consumption.size.quantity', 'yarn_acc_id')
    variant_mapping_ids = fields.One2many('material.consumption.variant.mapping', 'yarn_acc_mapping_id')
	
    product_tmp_id = fields.Many2one('product.template', string='Product', required=True)

    variant_ids = fields.Many2many(comodel_name='product.attribute.value',
                        relation='prod_attr_mat_cons_rel',
                        column1='mc_id',
                        column2='attr_id', string='Variants', required=True)
    uom_id = fields.Many2one('product.uom', string='UoM', required=True)
   
    preffered_supplier_id = fields.Many2one('res.partner', string="Pref. Supp.", readonly=True)
    buyer_mentioned_supplier_id = fields.Many2one('res.partner', string="Nom. Supp.")
    
    mc_yarn_id = fields.Many2one('material.consumption', ondelete="cascade")
    mc_acc_id = fields.Many2one('material.consumption', ondelete="cascade")

    # All kinds of constraints
    
    @api.multi
    def _validate_data(self, value):
        msg , filterInt, filterNum = {}, {}, {}
        
        filterNum['Quantity'] = value.get('quantity', False)
        filterInt['Wastage'] = value.get('wastage', False)

        
        msg.update(validator._validate_percentage(filterInt))
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        
        return super(MaterialConsumptionDetails, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(MaterialConsumptionDetails, self).write(vals)

    
    @api.onchange('product_tmp_id')
    def _onchange_product_id(self):
        res = {'domain': {'variant_ids': []}}
        self.uom_id=0
        self.variant_ids = 0
        if self.product_tmp_id:
            var_value = []
            for prod in self.product_tmp_id.product_variant_ids:
                for val in prod.attribute_value_ids:
                    var_value.append(val.id)
                self.uom_category = self.product_tmp_id.uom_id.category_id

            res['domain'] = {
                    'variant_ids': [('id', 'in', var_value)],
            }
           
        return res
    
    
    
    @api.onchange('variant_ids')
    def _onchange_variant_ids(self):
        res = {'domain': {'variant_ids': []}}

        set_attr_val = []
        for prod in self.product_tmp_id.product_variant_ids:
            for val in prod.attribute_value_ids:
                set_attr_val.append(val.id) 
                    
        if self.variant_ids:
            val_variants = []
            var_value = []
            
            for val in self.variant_ids:
                for attr in val.attribute_id:
                    if attr.id not in val_variants:
                        val_variants.append(attr.id)
                        
                       
                        
            for prod in self.product_tmp_id.attribute_line_ids:
                for val in prod.attribute_id:
                    if val.id not in val_variants:
                         for attr_val in val.value_ids:
                             if attr_val.id in set_attr_val:
                                 var_value.append(attr_val.id)
        else:
            var_value = set_attr_val                        
            
        res['domain'] = {
                    'variant_ids': [('id', 'in', var_value)]
        }    
            
        return res
    
        
