from odoo import fields, models, api


class InheritedStockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('picking_type_id')
    def calc_type_code(self):
        for rec in self:
            if rec.picking_type_id:
                rec.type_code = rec.picking_type_id.code

    type_code = fields.Char(compute='calc_type_code', store=True)
