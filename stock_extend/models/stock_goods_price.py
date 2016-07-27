from openerp import api, exceptions, fields, models

class StockGoodsPrice(models.Model):
    _name = 'stock.goods.price'
    
    product_id = fields.Many2one('product.product', string="Product", required=True, readonly=True, states={'draft':[('readonly', False)]})
    quantity = fields.Float(digits=(20, 2), string='Quantity', required=True, default=0.0, readonly=True, states={'draft':[('readonly', False)]})
    uom = fields.Many2one('product.uom', string="UOM", required=True, readonly=True, states={'draft':[('readonly', False)]}, related='product_id.uom_id')
    unit_price = fields.Float(digits=(20, 4), string='Unit Price', required=True, readonly=True, states={'draft':[('readonly', False)]})
    currency = fields.Many2one('res.currency', string="Currency", ondelete='set null', readonly=True, states={'draft':[('readonly', False)]}, default=lambda self: self.env.user.company_id.currency_id.id)
    cost_date = fields.Date(default=fields.Date.today(), string="Date", required=True, readonly=True, states={'draft':[('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed")],
                            default="draft", readonly=True, track_visibility='onchange')


    _sql_constraints = [
        ('check_quantity', "CHECK(quantity > 0.00)", "Quantity must be greater than zero..")
    ]
    
    @api.multi
    def action_submit(self):
        for obj in self:
           obj.product_id.product_tmpl_id.write({'standard_price':obj.unit_price})
           obj.state = 'confirmed'
        
