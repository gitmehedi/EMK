from odoo import api, fields, models,_
import time

class LCStatusWizard(models.TransientModel):
    _name = 'lc.status.wizard'

    status = fields.Selection([
        ('product', 'Product Wise'),
        ('variant', 'Variant Wise '),
    ], string="Type")

    product_temp_id = fields.Many2one('product.template', string='Product')
    product_id = fields.Many2one('product.product', string='Product(variant)')

    @api.onchange('status')
    def _product(self):
        self.product_temp_id= None
        self.product_id= None

    @api.multi
    def process_print(self):
        data = {}
        data['product_id'] = self.product_id.id
        data['product_name'] = self.product_id.name
        data['product_temp_id'] = self.product_temp_id.id
        data['product_temp_name'] = self.product_temp_id.name
        data['status'] = self.status
        data['product_temp_name'] = self.product_temp_id.name

        return self.env['report'].get_action(self, 'lc_sales_product_foreign.lc_status_foreign_template', data=data)
