# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _default_location_id(self):
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id),('operating_unit_id','=',self.env.user.default_operating_unit_id.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (self.env.user.company_id.name,))

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    location_id = fields.Many2one(
        'stock.location', 'Inventoried Location',
        readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        default=_default_location_id)
