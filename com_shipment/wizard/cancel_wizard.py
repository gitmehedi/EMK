from odoo import api, fields, models


class CancelWizard(models.TransientModel):
    _name = 'cancel.wizard'

    comments = fields.Text('Comments', required=True, help="Would you like to leave a message?")

    @api.multi
    def save_done(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        for product_line in shipment_obj.shipment_product_lines:
            lc_product_line_obj = self.env['lc.product.line'].search([('lc_id', '=', product_line.shipment_id.lc_id.id), ('sale_order_id', '=', product_line.sale_order_id.id)])
            lc_product_line_obj.write({'product_received_qty': lc_product_line_obj.product_received_qty-product_line.product_qty})
        shipment_obj.write(
            {'comment': self.comments, 'state': 'cancel'})
        return {'type': 'ir.actions.act_window_close'}

