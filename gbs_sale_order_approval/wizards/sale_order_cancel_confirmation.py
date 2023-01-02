from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class SaleOrderCancelConfirmation(models.TransientModel):
    _name = 'sale.order.cancel.confirmation'

    message = fields.Text('Message')

    def action_yes(self):
        sale_order_id = self._context['sale_order_id']
        sale_order_obj = self.env['sale.order'].browse(sale_order_id)

        #************************* Check pre condition
        if sale_order_obj:
            dc_objs = self.env['stock.picking'].search([('origin', '=', sale_order_obj.name)])
            for dc_obj in dc_objs:
                if dc_obj.state == 'done':
                    raise UserError('You cannot cancel sale orders whose goods are already delivered!')

            # *************************  Execution
            for dc_obj in dc_objs:
                dc_obj.do_unreserve()
                dc_obj.write({'state': 'cancel'})

                stock_move_objs = self.env['stock.move'].search([('picking_id', '=', dc_obj.id)])
                for sm_obj in stock_move_objs:
                    sm_obj.write({'state': 'cancel'})


            da_objs = self.env['delivery.authorization'].search([('sale_order_id', '=', sale_order_obj.id)])
            for da_obj in da_objs:
                da_obj.write({'state': 'refused'})

            do_objs = self.env['delivery.order'].search([('sale_order_id', '=', sale_order_obj.id)])
            for do_obj in do_objs:
                do_obj.write({'state': 'refused'})

        return sale_order_obj.write({'state': 'cancel'})

    def action_no(self):
        return {'type': 'ir.actions.act_window_close'}
