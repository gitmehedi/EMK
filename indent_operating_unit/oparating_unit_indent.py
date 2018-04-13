from odoo import fields, models, api

class OperatingUnitIndent(models.Model):
    _inherit = 'indent.indent'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)


    def _prepare_indent_picking(self):
        pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
        res = {
            'invoice_state': 'none',
            'picking_type_id': self.picking_type_id.id,
            'priority': self.requirement,
            'name': pick_name,
            'origin': self.name,
            'date': self.indent_date,
            # 'type': 'internal',
            'move_type': self.move_type,
            'partner_id': self.indentor_id.partner_id.id or False,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'location_dest_id': self.stock_location_id.id,
            'operating_unit_id': self.operating_unit_id.id
        }
        if self.company_id:
            res = dict(res, company_id=self.company_id.id)
        return res