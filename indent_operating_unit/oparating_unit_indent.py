from odoo import fields, models, api

class OperatingUnitIndent(models.Model):
    _inherit = 'indent.indent'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.model
    def _create_picking_and_moves(self):
        res = super(OperatingUnitIndent, self)._create_picking_and_moves()
        if res and self.operating_unit_id:
            picking_objs = self.env['stock.picking'].search([('id', '=', res)])
            picking_objs.write({'operating_unit_id': self.operating_unit_id.id})
        return res