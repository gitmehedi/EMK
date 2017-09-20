from odoo import api, fields, models, exceptions, _

class MrpDailyProductionLine(models.Model):
    _name = 'mrp.daily.production.line'
    _description = 'MRP daily production line'

    product_id = fields.Many2one('product.template', string="Product", ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UOM",ondelete='cascade')
    quantity = fields.Integer(string="Quantity", required=True)

    """ Relational Fields """
    parent_id = fields.Many2one('mrp.daily.production', ondelete='cascade')


    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')

