# imports of odoo
from odoo import api, fields, models, _


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=1,
                                        domain=lambda self: [("id", "in", self.env.user.operating_unit_ids.ids)],
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        if self.operating_unit_id:
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'mrp_operation'),
                ('operating_unit_id', '=', self.operating_unit_id.id),
                ('warehouse_id.company_id', 'in',
                 [self.env.context.get('company_id', self.env.user.company_id.id), False])],
                limit=1)
            self.picking_type_id = picking_type.id

    @api.onchange('mo_id')
    def onchange_mo_id(self):
        super(MrpUnbuild, self).onchange_mo_id()
        if self.mo_id:
            self.operating_unit_id = self.mo_id.operating_unit_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(MrpUnbuild, self).onchange_product_id()
        if self.mo_id:
            self.operating_unit_id = self.env.user.default_operating_unit_id

    @api.model
    def create(self, vals):
        if vals.get('mo_id', False):
            mo = self.env['mrp.production'].search([('id', '=', vals['mo_id'])])
            vals['operating_unit_id'] = mo.operating_unit_id.id

        if not vals.get('name'):
            ou = self.env['operating.unit'].search([('id', '=', vals['operating_unit_id'])])
            vals['name'] = self.env['ir.sequence'].next_by_code_new('mrp.unbuild', None, ou) or _('New')

        location = self.env.ref('stock.stock_location_stock')
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('operating_unit_id', '=', vals['operating_unit_id']),
            ('warehouse_id.company_id', 'in',
             [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1)

        vals['picking_type_id'] = picking_type.id
        vals['location_id'] = picking_type.default_location_src_id.id or location.id
        vals['location_dest_id'] = picking_type.default_location_dest_id.id or location.id

        return super(MrpUnbuild, self).create(vals)
