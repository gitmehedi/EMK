from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class BOMConsumption(models.Model):
    """
    Bill of Materials Consumption create BOM depending on Material Consumption and Buyer Work Order quantity.
    """
    _name = 'bom.consumption'
    
    """Product Style fields"""
    name = fields.Char(size=30, string="Serial No", readonly=True)
    bill_code = fields.Char(string='Code')
    
    """Model Relationship"""
    mc_id = fields.Many2one('material.consumption', string="Material Consumption", required=True,
                            domain=[('state', '=', 'confirm')])
    style_id = fields.Many2one('product.style', string="Style", required=True,
                               domain=[('visible', '=', 'True'), ('state', '=', 'confirm')])
    export_po_id = fields.Many2one('buyer.work.order', string="Work Order No", required=True,
                                  domain=[('state', '=', 'confirm')])
    
    
    yarn_ids = fields.One2many('bom.consumption.line', 'mc_yarn_id', string="Yarn", readonly=True)
    acc_ids = fields.One2many('bom.consumption.line', 'mc_acc_id', string="Accessories", readonly=True)
    
    
    """All function which process data and operation"""
        
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('bill_code')
            
        return super(BOMConsumption, self).create(vals)

    """All function which process data and operation"""
    
    @api.onchange('mc_id')
    def _onchange_mc_id(self):
        res,ids = {},[]
        self.style_id = 0
        self.export_po_id = 0
        if self.mc_id:
            res['domain'] = {
                    'style_id':[('id', 'in', self.mc_id.style_id.ids)],
            }

        return res
    
    @api.onchange('style_id')
    def _onchange_style_id(self):
        self.export_po_id = 0
    
    
    @api.multi
    def generate_bom(self):
        bwo_obj = self.env['buyer.work.order']
        mc_obj = self.env['material.consumption']
        mcbl_obj = self.env['bom.consumption.line']
        
        style_id = self.export_po_id.style_id.id
        bwo_data = bwo_obj.search([('id', '=', self.export_po_id.id)])
        mc_data = mc_obj.search([('id', '=', self.mc_id.id)])
        
        """ unlink existed data from child table """
        self.yarn_ids.unlink()
        self.acc_ids.unlink()
        
        
        if mc_data:
            data = mc_data[0]
        else:
            raise exceptions.ValidationError(validator.msg['mc_data'])
        
        if not bwo_data.bwo_product_ids:
            raise exceptions.ValidationError(validator.msg['bwo_data'])


        if data.yarn_ids:
            colors = bwo_data._get_attr_val_list('color')
            sizes = bwo_data._get_attr_val_list('size')    
            for line in data.yarn_ids:
                
                if line.finish_goods: 
                    """ If bom generate as per finish goods color.It will generate multiple
                     rows of product with exact color variant of BWO """
                    print "Call---------------------------1"
                    self.gen_finish_goods(line, bwo_data, colors, sizes) 
                     
                elif line.variant_mapping_ids:
                    """ If bom generate as per variant mapping.It will generate multiple
                     rows of product with exact variants of BWO """
                    
                    self.gen_size_wise_mapping(line, bwo_data, colors, sizes) 
                        
                elif line.size_qty_ids:
                    """ If size attribute given. It will generate single rows with exact product variants """
                    self.gen_size_wise_quantity(line, bwo_data, colors, sizes)
                else:
                    """ All regular case. It will generate single rows with exact product variants """
                    self.gen_regular(line, bwo_data, colors, sizes)
                    
        if data.acc_ids:
            for line in data.acc_ids:
                
                if line.finish_goods:
                    """ If bom generate as per finish goods.It will generate multiple
                     rows of product with exact variants of BWO """
                    self.gen_finish_goods(line, bwo_data, colors, sizes, flag='acc')
                    
                elif line.variant_mapping_ids:
                    """ If bom generate as per variant mapping.It will generate multiple
                     rows of product with exact variants of BWO """
                    self.gen_size_wise_mapping(line, bwo_data, colors, sizes, flag='acc') 
                    
                elif line.size_qty_ids:
                    """ If size attribute given. It will generate single rows with exact product variants """
                    self.gen_size_wise_quantity(line, bwo_data, colors, sizes, flag='acc')
                    
                else:
                    """ All regular case. It will generate single rows with exact product variants """
                    self.gen_regular(line, bwo_data, colors, sizes, flag='acc')
        
        
        self.unlink_duplicate_product(self.yarn_ids)
        self.unlink_duplicate_product(self.acc_ids)

        
        return {'type': 'ir.actions.act_window_close'}
    
    def unlink_duplicate_product(self, line):
        if line:
            rm_line = []  
            for yarn in line:
                sum, count = 0, 0
            
                for yarn_ids in line:
                    if yarn.product_id.id == yarn_ids.product_id.id:
                        count = count + 1
                        if count > 1:
                            sum = yarn.quantity + yarn_ids.quantity
                            rm_line.append(yarn_ids.id)
                            yarn.write({'quantity': sum})
            
            if len(rm_line) > 0:
                for yarn in line:
                    if yarn.id in rm_line:
                        yarn.unlink()   
        return True
    
    def gen_finish_goods(self, line, bwo_data, colors, sizes, flag='yarn'):
        
        if line.variant_mapping_ids:
            print "Call---------------------------2"
            for bwo_val in bwo_data.bwo_product_ids:
                line.prod_id = self.get_products_id(line, bwo_val, False, 'goods')
                line.total_qty = self.calculate_quantity(line, bwo_val, 200, sizes)
                
                if line.prod_id:  
                    self.bom_generate(line, flag) 
        else:
            print "Call---------------------------3"
            for  key, value in colors.iteritems():
                line.prod_id = self.get_products_id(line, bwo_data, key, 'goods')
                line.total_qty = self.calculate_quantity(line, bwo_data, value, sizes)
                
                if line.prod_id:  
                    self.bom_generate(line, flag)
                
    def gen_size_wise_quantity(self, line, bwo_data, lists, size_lists, flag='yarn'): 
            
        line.prod_id = self.get_products_id(line, bwo_data, line.variant_ids.ids, 'else')
         
        qty = sum(lists.values())
        line.total_qty = self.calculate_quantity(line, bwo_data, qty, size_lists)
         
        if line.prod_id:
            self.bom_generate(line, flag)
            
    def gen_size_wise_mapping(self, line, bwo_data, colors, sizes, flag='yarn'):
        print colors, "----", sizes
        for bwo_val in bwo_data.bwo_product_ids:
            line.prod_id = self.get_products_id(line, bwo_val, False, 'map')
            line.total_qty = self.calculate_quantity(line, bwo_val, False, sizes) 
    
                
        if line.prod_id:  
            self.bom_generate(line, flag)
                
    def gen_regular(self, line, bwo_data, lists, size_lists, flag='yarn'):
        
        variant_id = list(set(line.variant_ids.ids) & set(lists.keys()))
        line.prod_id = self.get_products_id(line, bwo_data, line.variant_ids.ids)  
          
        qty = sum(lists.values())
        line.total_qty = self.calculate_quantity(line, bwo_data, qty)
        
        if line.prod_id: 
            self.bom_generate(line, flag)
     
                        
    def get_products_id(self, mc_obj, bwo_obj, variant_id, tags='all'):
        prod_obj = self.env['product.product']
        gen_prod_obj = prod_obj.search([('product_tmpl_id', '=', mc_obj.product_tmp_id.id)])
        size_list = self.env['product.attribute'].search([('is_size', '=', True)])
        color_list = self.env['product.attribute'].search([('is_color', '=', True)])
        product_id = False
        attr_size = 0

        
        if mc_obj.finish_goods:
            if mc_obj.variant_mapping_ids:
                """
                    1.Loop over Buyer Work Order using bwo_obj.bwo_product_ids 
                    2.Loop over Material Consumption variant_mapping_ids
                    3.Again Loop over variant_mapping_ids.prod_variant_ids.
                    4.Get all attributes of this variant
                    5.Remove variants from mc_varinats
                    6.Continue it end of the loop.
                """
                
                bwo_size_attr = set(list(set(size_list.value_ids.ids).intersection(bwo_obj.product_id.attribute_value_ids.ids)))
                mc_variant_ids = mc_obj.variant_ids.ids
                bwo_variant_ids = bwo_obj.product_id.attribute_value_ids.ids
                
                for mc_attr in mc_obj.variant_mapping_ids:
                    mc_size_exist = list(bwo_size_attr.intersection(mc_attr.attr_size_id.ids))
                    if len(mc_size_exist) > 0:
                        
                        for prod_var_attr in mc_attr.prod_variant_ids.ids:
                            attr = self.env['product.attribute.value'].search([('id', '=', prod_var_attr)])
                            mc_variant_ids = list(set(mc_variant_ids) - set(attr.attribute_id.value_ids.ids))
                            bwo_variant_ids = list(set(bwo_variant_ids) - set(attr.attribute_id.value_ids.ids))
                            
                        merge_attr = list(set(bwo_variant_ids + mc_attr.prod_variant_ids.ids)) 
                        for rmv in merge_attr:
                            attr_new = self.env['product.attribute.value'].search([('id', '=', rmv)])
                            mc_variant_ids = list(set(mc_variant_ids) - set(attr_new.attribute_id.value_ids.ids))
                                
                        merge_attr = set(merge_attr + mc_variant_ids + bwo_variant_ids)
                            
                        for obj in gen_prod_obj:
                            com_attr = set(list(set(merge_attr).intersection(obj.attribute_value_ids.ids)))
                            if len(com_attr) > attr_size:
                                attr_size = len(com_attr)
                                product_id = obj.id
            else:    
                rm_color = list(set(mc_obj.variant_ids.ids) - set(color_list.value_ids.ids))
                
                for bwo_val in bwo_obj.bwo_product_ids:
                    for obj in gen_prod_obj:
                        print bwo_val.product_id.attribute_value_ids.ids, "Call---------------------------4---2", color_list.value_ids.ids
                        get_com_attr = list(set(list(set(bwo_val.product_id.attribute_value_ids.ids).intersection(color_list.value_ids.ids))))
                        merge_attr = list(set(rm_color + get_com_attr))
                        if (variant_id in obj.attribute_value_ids.ids):     
                            
                            com_attr = set(list(set(merge_attr).intersection(obj.attribute_value_ids.ids)))
                            if len(com_attr) > attr_size:
                                attr_size = len(com_attr)
                                product_id = obj.id
                                
        elif mc_obj.variant_mapping_ids:    
           for mc_attr in mc_obj.variant_mapping_ids:
               if variant_id in mc_attr.attr_size_id.ids:
                   merge_attr = set(mc_attr.attr_size_id.ids + mc_attr.prod_variant_ids.ids)
                   for obj in gen_prod_obj:
                        com_attr = set(list(merge_attr.intersection(obj.attribute_value_ids.ids)))
                        if len(com_attr) > attr_size:
                            attr_size = len(com_attr)
                            product_id = obj.id
        elif mc_obj.size_qty_ids:
            for obj in gen_prod_obj:
                com_attr = set(list(set(variant_id).intersection(obj.attribute_value_ids.ids)))
                if len(com_attr) > attr_size:
                    attr_size = len(com_attr)
                    product_id = obj.id 
        
        else:
            for obj in gen_prod_obj:
                if (set(variant_id) == set(list(set(variant_id).intersection(obj.attribute_value_ids.ids)))):
                    product_id = obj.id
                    return product_id            
                       
        return product_id
    
    def calculate_quantity(self, mc_obj, bwo_data, qty, lists=True):
        consumption_for = 12
        sum = 0
        
        if mc_obj.finish_goods:
            if mc_obj.variant_mapping_ids:
                wastage_cal = (bwo_data.qty * mc_obj.quantity)
                cal_after_was = wastage_cal + (wastage_cal * (mc_obj.wastage / 100)) 
                total = cal_after_was + (cal_after_was * (bwo_data.bwo_details_id.tolerance / 100))
            else:
                wastage_cal = qty * mc_obj.quantity
                cal_after_was = wastage_cal + (wastage_cal * (mc_obj.wastage / 100)) 
                total = cal_after_was + (cal_after_was * (bwo_data.tolerance / 100))
                
        elif mc_obj.variant_mapping_ids:
            for size in mc_obj.variant_mapping_ids:
                if qty == size.attr_size_id.id:
                    sum = sum + (lists[qty] * mc_obj.quantity)
            wastage_cal = sum
            cal_after_was = wastage_cal + (wastage_cal * (mc_obj.wastage / 100)) 
            total = cal_after_was + (cal_after_was * (bwo_data.bwo_details_id.tolerance / 100))
            
        elif mc_obj.size_qty_ids:
            for mc_prod in bwo_data.bwo_product_ids:
                for data in mc_prod.product_id.attribute_value_ids:
                    for size in mc_obj.size_qty_ids:
                        if data.id == size.attr_size_id.id:
                            sum = sum + (mc_prod.qty * size.quantity)
            wastage_cal = sum
            cal_after_was = wastage_cal + (wastage_cal * (mc_obj.wastage / 100)) 
            total = cal_after_was + (cal_after_was * (bwo_data.tolerance / 100))
        else:    
            wastage_cal = qty * mc_obj.quantity
            cal_after_was = wastage_cal + (wastage_cal * (mc_obj.wastage / 100)) 
            total = cal_after_was + (cal_after_was * (bwo_data.tolerance / 100))
        
        
        return total
    
    def bom_generate(self, obj, flag='acc'):
        mcbl_obj = self.env['bom.consumption.line']
        vals = {}
        
        if flag == 'acc':
            vals['mc_acc_id'] = self.id
        else:
            vals['mc_yarn_id'] = self.id
                
        vals['product_id'] = obj.prod_id
        vals['uom_id'] = obj.uom_id.id
        vals['quantity'] = obj.total_qty
        vals['preffered_supplier_id'] = obj.preffered_supplier_id.id
        vals['buyer_mentioned_supplier_id'] = obj.buyer_mentioned_supplier_id.id
        vals['status'] = obj.status
        
                           
        return mcbl_obj.create(vals)
        
            
    
