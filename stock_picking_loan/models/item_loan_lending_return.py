from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LoanLending(models.Model):
    _inherit = 'item.loan.lending'

    @api.multi
    def action_view_picking(self):
        product_list = self.item_lines.filtered(lambda o: o.due_qty > 0.0)

        if not product_list:
            raise UserError('No Due so no need any adjustment!!!')

        stock_picking_objs = self.env['stock.picking'].search([('loan_id','=',self.id)])
        if stock_picking_objs:
            result = self.env.ref('stock.action_picking_tree_all').read()[0]
            result['domain'] = [('id','in', stock_picking_objs.ids)]
        else:
            picking_type_objs = self.env['stock.picking.type'].search(
                [('warehouse_id.operating_unit_id', '=', self.env.user.default_operating_unit_id.id),
                 ('code', '=', 'incoming')])
            location_id = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1).id

            res = self.env.ref('stock_picking_extend.view_stock_picking_form1')

            result = {
                'name': _('Stock'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': res and res.id or False,
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'context': {'default_picking_type_id': picking_type_objs[0].id,
                            'default_location_id' : location_id,
                            'default_transfer_type': 'receive',
                            'default_receive_type': 'loan',
                            'default_loan_id': self.id,
                            },
            }

        return result
