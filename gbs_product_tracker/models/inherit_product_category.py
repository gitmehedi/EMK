from odoo import api, fields, models, tools, _


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ['product.category', 'mail.thread']

    name = fields.Char('Name', index=True, required=True, translate=True,track_visibility='onchange')
    parent_id = fields.Many2one('product.category', 'Parent Category', index=True, ondelete='cascade',track_visibility='onchange')
    type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal')], 'Category Type', default='normal',track_visibility='onchange',
        help="A category of the view type is a virtual category that can be used as the parent of another category to create a hierarchical structure.")

    property_valuation = fields.Selection([
        ('manual_periodic', 'Periodic (manual)'),
        ('real_time', 'Perpetual (automated)')], string='Inventory Valuation',
        company_dependent=True, copy=True, required=True,track_visibility='onchange',
        help="If perpetual valuation is enabled for a product, the system "
             "will automatically create journal entries corresponding to "
             "stock moves, with product price as specified by the 'Costing "
             "Method'. The inventory variation account set on the product "
             "category will represent the current inventory value, and the "
             "stock input and stock output account will hold the counterpart "
             "moves for incoming and outgoing products.")

    route_ids = fields.Many2many(
        'stock.location.route', 'stock_location_route_categ', 'categ_id', 'route_id', 'Routes',track_visibility='onchange',
        domain=[('product_categ_selectable', '=', True)])
    removal_strategy_id = fields.Many2one(
        'product.removal', 'Force Removal Strategy',track_visibility='onchange',
        help="Set a specific removal strategy that will be used regardless of the source location for this product category")