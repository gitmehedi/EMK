from odoo import fields, models, api
from odoo.tools import frozendict


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

    @api.multi
    def action_view_picking(self):
        # Add operating unit in the context
        self._add_operating_unit_in_context(self.operating_unit_id.id)
        return super(OperatingUnitIndent, self).action_view_picking()

    def _add_operating_unit_in_context(self, operating_unit_id=False):
        """ Adding operating unit in context. """
        if operating_unit_id:
            context = dict(self.env.context)
            context.update({'operating_unit_id': operating_unit_id})
            self.env.context = frozendict(context)

    @api.model
    def create(self, vals):
        self._add_operating_unit_in_context(vals.get('operating_unit_id'))
        return super(OperatingUnitIndent, self).create(vals)
