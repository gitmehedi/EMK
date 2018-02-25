from odoo import api, fields, models

class MrpDailyProductionLine(models.Model):
    _name = 'mrp.daily.production.line'
    _description = 'MRP daily production line'

    product_id = fields.Many2one('product.product', string="Product", ondelete='cascade', required=True)

    uom_id = fields.Many2one(
        'product.uom', string="UoM", domain=[
            ('category_id', '=', 2)], required=True,ondelete='cascade')
    quantity = fields.Integer(string="Quantity", required=True)

    """ Relational Fields """
    parent_id = fields.Many2one('mrp.daily.production', ondelete='cascade')


    # state = fields.Selection([
    #     ('draft', "Draft"),
    #     ('applied', "Applied"),
    #     ('approved', "Approved"),
    # ], default='draft')

