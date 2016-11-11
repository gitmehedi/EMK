from openerp import api, fields, models


    

class ProductCostAdjustment(models.Model):
    _name = 'product.cost.adjustment'
    
    name = fields.Char (string='Inventory Reference',required=True)

    inventory_date = fields.Datetime(string='Date', required=True, readonly=True,
                                 default = fields.Datetime.now)
    product_tmp_id = fields.Many2one('product.template', string='Product', required=True)
    cost_adjustment_ids = fields.One2many('product.cost.adjustment.line', 'cost_adjustment_id')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('done', 'Validated'),
    ], default='draft', string="Status")



    # @api.onchange('product_tmp_id')
    # def _onchange_product_tem_id(self):
    #     if self.product_tmp_id:
    #
    # """ onchange fields """
    #
    # @api.onchange('buyer_id')
    # def _onchange_buyer_id(self):
    #     res, ids = {}, []
    #     self.style_id = 0
    #     self.buyer_department = 0
    #
    #     if self.buyer_id:
    #         for obj in self.buyer_id.styles_ids:
    #             if obj.version == 1 and obj.state == 'confirm':
    #                 ids.append(obj.id)
    #
    #     res['domain'] = {
    #         'style_id': [('id', 'in', ids)],
    #     }
    #
    #     return res