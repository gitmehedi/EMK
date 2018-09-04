from odoo import api, fields, models, _


class SalesChannel(models.Model):
    _name = "sales.channel"

    name = fields.Char(string='Name', required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)
    employee_id = fields.Many2one('res.users', string='Approver Manager', required=False)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True,)

    @api.onchange('operating_unit_id')
    def _onchange_OP_unit(self):
        return {'domain': {'warehouse_id': [('operating_unit_id', '=', self.operating_unit_id.id)]}}

