from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class SaleOrderCancelConfirmation(models.TransientModel):
    _name = 'sale.order.cancel.confirmation'

    message = fields.Text('Message')

    def action_yes(self):
        sale_order_id = self._context['sale_order_id']
        sale_order_obj = self.env['sale.order'].browse(sale_order_id)
        dc_objs = self.env['stock.picking'].sudo().search([('origin', '=', sale_order_obj.name)])

        #************************* Check pre condition
        for dc_obj in dc_objs:
            if dc_obj.state == 'done':
                raise UserError('You cannot cancel sale orders whose goods are already delivered!')


        # *************************  Execution
        for dc_obj in dc_objs:
            dc_obj.write({'state': 'cancel'})

        da_objs = self.env['delivery.authorization'].sudo().search([('sale_order_id', '=', sale_order_obj.id)])
        for da_obj in da_objs:
            da_obj.write({'state': 'refused'})

        return sale_order_obj.write({'state': 'cancel'})

    def action_no(self):
        return {'type': 'ir.actions.act_window_close'}
