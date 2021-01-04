# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_continue = fields.Boolean('Continue Production', default=True)

    @api.multi
    @api.depends('workorder_ids.state', 'move_finished_ids')
    def _get_produced_qty(self):
        res = super(MrpProduction, self)._get_produced_qty()
        for production in self:
            if not production.production_continue and (production.state not in ('done', 'cancel')):
                production.check_to_done = True

        return res

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            product_product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product_product.uom_id.id

        return super(MrpProduction, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'product_id' in vals:
            product_product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product_product.uom_id.id

        return super(MrpProduction, self).write(vals)
