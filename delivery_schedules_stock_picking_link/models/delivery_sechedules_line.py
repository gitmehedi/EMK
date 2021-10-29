from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeliverySchedulesLine(models.Model):
    _inherit = 'delivery.schedules.line'

    stock_picking_id = fields.Many2one('stock.picking', string='Picking Reference')

    @api.multi
    def action_delivery(self):
        # Validation
        if self.requested_date > fields.Datetime.now():
            text = 'Requested Date cannot be greater than today.'
            wizard = self.env['message.box.wizard'].create({'text': text})
            return self.get_warning_message_wizard(wizard.id)

        # get picking linked with sale order
        picking = self.sale_order_id.mapped('picking_ids').filtered(
            lambda i: i.state not in ['done', 'cancel'] and i.picking_type_id.code == 'outgoing'
        )

        if not picking:
            self.write({'state': 'cancel'})
            text = 'No remaining qty for delivery.'
            wizard = self.env['message.box.wizard'].create({'text': text})
            return self.get_warning_message_wizard(wizard.id)

        # check qty availability
        if picking.state != 'assigned':
            picking.action_assign()

        # if qty is not available in the stock, notify the user with a message
        if picking.state not in ['assigned', 'partially_available'] or \
                picking.pack_operation_product_ids[0].product_qty < self.scheduled_qty:
            text = 'Unable to Deliver Goods due to qty is not available in current stock.'
            wizard = self.env['message.box.wizard'].create({'text': text})
            return self.get_warning_message_wizard(wizard.id)

        if not picking.pack_operation_product_ids:
            text = 'You cannot do that on a DC that does not have any operations line.'
            wizard = self.env['message.box.wizard'].create({'text': text})
            return self.get_warning_message_wizard(wizard.id)

        # remainder: should be done for multiple pack operation lines
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
        action['context'] = {
            'search_default_picking_type_id': [self.stock_picking_id.picking_type_id.id],
            'default_picking_type_id': self.stock_picking_id.picking_type_id.id,
            'contact_display': 'partner_address'
        }

        return action

    @api.multi
    def action_reset(self):
        self.write({'state': 'approve'})

    @api.multi
    def get_warning_message_wizard(self, wizard_id):
        return {
            'name': _('Warning Message'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.box.wizard',
            'target': 'new',
            'res_id': wizard_id
        }
