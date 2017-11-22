from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DocReceiveWizard(models.TransientModel):
    _name = 'doc.receive.wizard'

    bill_of_lading_number = fields.Char(string='BoL Number', required=True, help="Bill Of Lading Number")
    shipment_date = fields.Date('Ship on Board', required=True)

    # Packing List
    gross_weight = fields.Float('Gross Weight', required=True)
    net_weight = fields.Float('Net Weight', required=True)

    product_lines = fields.One2many('shipment.product.line.wizard', 'shipment_id', string='Product(s)')
    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment',
                                  default=lambda self: self.env.context.get('active_id'))


    @api.onchange('shipment_id')
    def po_product_line(self):
        self.product_lines = []
        vals = []
        for obj in self.shipment_id.shipment_product_lines:
            vals.append((0, 0, {'product_id': obj.product_id,
                                'lc_pro_line_id': obj.lc_pro_line_id,
                                'shipment_pro_line_id': obj.id,
                                'name': obj.name,
                                'product_qty': obj.product_qty,
                                'currency_id': obj.currency_id,
                                'date_planned': obj.date_planned,
                                'product_uom': obj.product_uom
                                }))
        self.product_lines = vals

    @api.multi
    def save_doc_receive(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'bill_of_lading_number': self.bill_of_lading_number,
                            'shipment_date': self.shipment_date,
                            'gross_weight': self.gross_weight,
                            'net_weight': self.net_weight,
                            'state': 'receive_doc'})
        for pro_line in self.product_lines:

            pro_line_pool = self.env['shipment.product.line'].search([('id','=',pro_line.shipment_pro_line_id)])
            print pro_line.product_qty , pro_line_pool.product_qty
            if pro_line.product_qty>pro_line_pool.product_qty:
                raise ValidationError(_("Receive Quantity Must be less then Actual Quantity."))
            else:
                pro_line_pool.write({'product_qty': pro_line.product_qty})

            pro_lc_line_pool = self.env['lc.product.line'].search([('id', '=', pro_line.lc_pro_line_id)])
            res_received_qty = pro_lc_line_pool.product_received_qty+pro_line.product_qty
            if pro_line.product_qty>pro_lc_line_pool.product_qty:
                raise ValidationError(_("Receive Quantity Must be less then Actual Quantity."))
            else:
                pro_lc_line_pool.write({'product_received_qty': res_received_qty})

        return {'type': 'ir.actions.act_window_close'}

class ShipmentProductLineWizard(models.Model):
    _name = 'shipment.product.line.wizard'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)

    product_qty = fields.Float(string='Quantity')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')

    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment')

    lc_pro_line_id = fields.Integer(string='LC Line ID')
    shipment_pro_line_id = fields.Integer(string='Shipment Line ID')









