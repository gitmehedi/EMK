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

    filter = fields.Selection(
        string='Inventory of', selection='_selection_filter',
        required=True,
        default='partial',
        help="If you do an entire inventory, you can choose 'All Products' and it will prefill the inventory with the current stock.  If you only do some products  "
             "(e.g. Cycle Counting) you can choose 'Manual Selection of Products' and the system won't propose anything.  You can also let the "
             "system propose for a single product / lot /... ")

    @api.model
    def _selection_filter(self):
        """ Get the list of filter allowed according to the options checked
        in 'Settings\Warehouse'. """
        res_filter = [
            ('none', _('All products')),
            ('category', _('One product category')),
            ('product', _('One product only')),
            ('partial', _('Select products manually'))]

        if self.user_has_groups('stock.group_tracking_owner'):
            res_filter += [('owner', _('One owner only')), ('product_owner', _('One product for a specific owner'))]
        if self.user_has_groups('stock.group_production_lot'):
            res_filter.append(('lot', _('One Lot/Serial Number')))
        if self.user_has_groups('stock.group_tracking_lot'):
            res_filter.append(('pack', _('A Pack')))
        return res_filter

    @api.onchange('operating_unit_id')
    def _compute_allowed_operating_unit_ids(self):
        domain = {}
        domain['operating_unit_id'] = [('id', 'in', self.env.user.operating_unit_ids.ids)]
        domain['location_id'] = [('usage', '=', 'internal'),('operating_unit_id', '=', self.operating_unit_id.id)]
        return {'domain': domain}

    @api.onchange('company_id')
    def _compute_allowed_company_ids(self):
        domain = {}
        domain['company_id'] = [('id', 'in', self.env.user.company_ids.ids)]
        return {'domain': domain}

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_location_default_select(self):
        for location in self:
            stock_warehouse = self.env['stock.warehouse'].search(
                [('operating_unit_id', '=', location.operating_unit_id.id)])
            location.location_id = stock_warehouse.wh_main_stock_loc_id