from odoo import api, fields, models, _


class FineshProduct(models.Model):
    _name = 'finish.product.line'

    product_id = fields.Many2one('product.template', 'Product Name')
    daily_pro_id = fields.Many2one('daily.production', 'Daily Production')
    fnsh_product_qty = fields.Float('Quantity')
    finish_product_date = fields.Date('Date')
    uom_id = fields.Many2one('product.uom', 'UOM')

    state = fields.Selection([

        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

    @api.onchange('product_id')
    def onchange_product(self):
        self.uom_id = self.product_id.uom_id
        self.finish_product_date = self.daily_pro_id.production_date




