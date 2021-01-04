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

    def _generate_raw_move(self, bom_line, line_data):
        move = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        product_uom_qty = move.product_uom_qty
        move.write({'standard_qty': product_uom_qty})

        return move

    @api.multi
    def _update_raw_move(self, bom_line, line_data):
        # overwrite the base model function
        quantity = line_data['qty']
        self.ensure_one()
        move = self.move_raw_ids.filtered(
            lambda x: x.bom_line_id.id == bom_line.id and x.state not in ('done', 'cancel'))
        if move:
            if quantity > 0:
                move[0].write({'standard_qty': quantity, 'product_uom_qty': quantity})
            else:
                if move[0].quantity_done > 0:
                    raise UserError(_(
                        'Lines need to be deleted, but can not as you still have some quantities to consume in them. '))
                move[0].action_cancel()
                move[0].unlink()
            return move
        else:
            self._generate_raw_move(bom_line, line_data)

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
