# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'mail.thread']

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
        domain="[('usage', '=', 'internal'),('operating_unit_id', '=',operating_unit_id)]",
        states={'draft': [('readonly', False)]},
        default=_default_location_id)

    @api.onchange('operating_unit_id')
    def _compute_allowed_operating_unit_ids(self):
        domain = {}
        domain['operating_unit_id'] = [('id', 'in', self.env.user.operating_unit_ids.ids)]
        domain['location_id'] = [('usage', '=', 'internal'),('operating_unit_id', '=', self.operating_unit_id.id)]
        return {'domain': domain}

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_location_default_select(self):
        for location in self:
            stock_warehouse = self.env['stock.warehouse'].search(
                [('operating_unit_id', '=', location.operating_unit_id.id)])
            location.location_id = stock_warehouse.wh_main_stock_loc_id