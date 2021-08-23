from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeliverySchedulesLine(models.Model):
    _inherit = 'delivery.schedules.line'

    stock_picking_id = fields.Many2one('stock.picking', string='Picking Reference')

    @api.multi
    def action_delivery(self):
        if self.requested_date > fields.Datetime.now():
            raise UserError(_('Requested Date cannot be greater than today.'))

        picking = self.sale_order_id.mapped('picking_ids').filtered(lambda i: i.state not in ['done', 'cancel'] and i.picking_type_id.code == 'outgoing')

        # check qty availability
        if picking.state != 'assigned':
            picking.action_assign()

        # if qty is not available in the stock, notify the user with a message
        if picking.state != 'assigned':
            raise UserError(_('Unable to Deliver Goods due to qty is not available in current stock.'))

        if not picking.pack_operation_product_ids:
            raise UserError(_("You cannot do that on a DC that does not have any operations line."))

        # for single operation product
        picking.pack_operation_product_ids[0].write({'qty_done': self.scheduled_qty})

        action = self.env.ref('stock.action_picking_form').read()[0]
        action['res_id'] = picking.id
        action['context'] = {
            'search_default_picking_type_id': [picking.picking_type_id.id],
            'default_picking_type_id': picking.picking_type_id.id,
            'contact_display': 'partner_address'
        }

        return action

    @api.multi
    def action_delivery_detail(self):
        action = self.env.ref('stock.action_picking_form').read()[0]
        action['res_id'] = self.stock_picking_id.id

        return action
