from openerp import api,models,fields

class ProductCustomVariant(models.Model):
    _name = 'product.custom.variant'
    name=fields.Char('Name')

    size_variant_ids=fields.One2many(comodel_name='product.product', inverse_name='size_variant_id')
    other_variant_ids=fields.One2many(comodel_name='product.product', inverse_name='other_variant_id')


class Product_Variant_Extend(models.Model):
    _inherit = 'product.product'

    size_variant_id=fields.Many2one(comodel_name='product.custom.variant')
    other_variant_id=fields.Many2one(comodel_name='product.custom.variant')

    # @api.multi
    # def name_get(self):
    #     return "%s - %s" % (self.name, self.default_code)


class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    def update_product_variant(self, product_tmp_id):
        product_all=self.env['product.template'].browse([product_tmp_id])
#         product_variants=self.env['product.product'].search(['|','&',('product_tmpl_id', '=', product_tmp_id),('active', '=', True),('active', '=', False)],order='id asc')
        for product in product_all.product_variant_ids:
            OtherVariant=""
            SizeVariant=""
            for attribute in product.attribute_value_ids.sorted():
                if attribute.attribute_id.name!='Size':
                    if len(OtherVariant)>0:
                        OtherVariant=OtherVariant+','
#                     OtherVariant=OtherVariant+attribute.attribute_id.name+':'+ attribute.name
                    OtherVariant=OtherVariant+attribute.name
                if attribute.attribute_id.name=='Size':
                    SizeVariant=attribute.name
#                     SizeVariant=attribute.attribute_id.name +':'+attribute.name

            size_is_exists=self.env['product.custom.variant'].search([('name','=',SizeVariant)])
            if len(size_is_exists)==0:
                size_res=self.env['product.custom.variant'].create({'name':SizeVariant})
            else:
                size_res= size_is_exists

            print size_res

            other_variant_is_exists=self.env['product.custom.variant'].search([('name','=',OtherVariant)])
            if len(other_variant_is_exists)==0:
                other_variant_res=self.env['product.custom.variant'].create({'name':OtherVariant})
            else:
                other_variant_res= other_variant_is_exists

            print other_variant_res

            product.write({
                           'size_variant_id':size_res.id,
                           'other_variant_id':other_variant_res.id
                           }
                          )

    @api.model
    def create(self, vals):
        product_template_id = super(InheritedProductTemplate, self).create(vals)
        self.update_product_variant(product_template_id.id)
        return product_template_id
    @api.multi
    def write(self,vals):
        #TODO: process before updating resource
        res = super(InheritedProductTemplate, self).write(vals)
        self.update_product_variant(self.id)
        return res
    