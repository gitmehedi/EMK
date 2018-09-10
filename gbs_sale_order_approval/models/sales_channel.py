from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SalesChannel(models.Model):
    _name = "sales.channel"

    name = fields.Char(string='Name', required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)
    user_id = fields.Many2one('res.users', string='Approver Manager', required=False)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True,)

    @api.onchange('operating_unit_id')
    def _onchange_OP_unit(self):
        return {'domain': {'warehouse_id': [('operating_unit_id', '=', self.operating_unit_id.id)]}}

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['sales.channel'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError("Sales Channel name must be unique!")
        