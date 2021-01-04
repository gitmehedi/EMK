from odoo import api, fields, models, _


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        # execute the parent function
        res = super(MrpProductProduce, self).do_produce()

        # check continue production
        done_moves = self.production_id.move_finished_ids.filtered(lambda x: x.state != 'cancel' and x.product_id.id == self.production_id.product_id.id)
        qty_produced = sum(done_moves.mapped('quantity_done'))

        if qty_produced < self.production_id.product_qty:
            # confirmation wizard view
            view = self.env.ref('mrp_extend.view_mrp_production_confirmation')
            wiz = self.env['mrp.production.confirmation'].create({'production_id': self.production_id.id})
            return {
                'name': _('Continue Production?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.production.confirmation',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        return res
