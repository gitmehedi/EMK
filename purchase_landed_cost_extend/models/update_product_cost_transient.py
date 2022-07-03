from odoo import fields, models, api, _


class UpdateProductCost(models.TransientModel):
    _name = 'update.product.cost'
    _description = 'Update Product Cost Transient'

    def _default_cost_line(self):
        line_id = self._context['line_id']
        return line_id

    cost_line = fields.Many2one('purchase.cost.distribution.line',  default =lambda self: self._default_cost_line())

    product_cost_per_unit = fields.Float(string='New Product Cost(Per Unit)')

    def update_cost(self):
        stock_move_utility = self.env['stock.move.utility']
        stock_move_utility.update_move_price_unit(False, self.cost_line.move_id, 'landed_cost_window_2', self.product_cost_per_unit,
                                                  False)

        message_id = self.env['landed.cost.success.wizard'].create({'message': _(
            "Product Cost (Per Unit) Successfully!")
        })
        return {
            'name': _('Success'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'landed.cost.success.wizard',
            'context': {'distribution_id': self.cost_line.distribution.id},
            'res_id': message_id.id,
            'target': 'new'
        }
