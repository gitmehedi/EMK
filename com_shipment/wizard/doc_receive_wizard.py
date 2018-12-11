from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DocReceiveWizard(models.TransientModel):
    _name = 'doc.receive.wizard'

    bill_of_lading_number = fields.Char(string='BoL Number', required=True, help="Bill Of Lading Number")
    shipment_date = fields.Date('Ship on Board', required=True)

    invoice_number = fields.Char(string='Invoice Number',required=True)
    invoice_value = fields.Float(string='Invoice Value' ,compute='_compute_invoice_value',required=True,store=True)

    # Packing List
    gross_weight = fields.Float('Gross Weight', required=True)
    net_weight = fields.Float('Net Weight', required=True)

    product_lines = fields.One2many('shipment.product.line.wizard', 'doc_shipment_id', string='Product(s)')
    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment',
                                  default=lambda self: self.env.context.get('active_id'))

    @api.constrains('product_lines')
    def _check_multiple_products_line(self):
        if not self.product_lines:
            raise ValidationError("You can't receive doc without products")

    @api.depends('product_lines.product_qty')
    def _compute_invoice_value(self):
        for record in self:
            record.invoice_value = sum([s.product_qty for s in record.product_lines])

    @api.onchange('shipment_id')
    def po_product_line(self):
        self.product_lines = []
        vals = []
        pro_lc_line_pool = self.env['lc.product.line'].search([('lc_id', '=', self.shipment_id.lc_id.id)])
        for obj in pro_lc_line_pool:
            product_qty = obj.product_qty - obj.product_received_qty
            if product_qty > 0:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'lc_pro_line_id': obj.id,
                                    'name': obj.name,
                                    'product_qty': product_qty,
                                    'currency_id': obj.currency_id,
                                    'date_planned': obj.date_planned,
                                    'product_uom': obj.product_uom,
                                    'price_unit': obj.price_unit,
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
                            'invoice_value': self.invoice_value,
                            'state': 'receive_doc'})
        vals = []
        for pro_line in self.product_lines:
            vals.append((0, 0, {'product_id': pro_line.product_id,
                            'name': pro_line.name,
                            'product_qty': pro_line.product_qty,
                            'currency_id': pro_line.currency_id,
                            'date_planned': pro_line.date_planned,
                            'product_uom':pro_line.product_uom,
                            'price_unit':pro_line.price_unit,
                            }))
            pro_lc_line_pool = self.env['lc.product.line'].search([('id', '=', pro_line.lc_pro_line_id)])
            res_received_qty = pro_lc_line_pool.product_received_qty+pro_line.product_qty
            if pro_line.product_qty>pro_lc_line_pool.product_qty:
                raise ValidationError(_("Receive Quantity Must be less then Actual Quantity."))
            else:
                pro_lc_line_pool.write({'product_received_qty': res_received_qty})

        self.shipment_id.shipment_product_lines = vals

        return {'type': 'ir.actions.act_window_close'}


class ShipmentProductLineWizard(models.TransientModel):
    _name = 'shipment.product.line.wizard'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 change_default=True, required=True)
    product_qty = fields.Float(string='Quantity')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')

    doc_shipment_id = fields.Many2one('doc.receive.wizard', string='Purchase Shipment', ondelete='cascade')
    price_unit = fields.Float(string='Unit Price')
    lc_pro_line_id = fields.Integer(string='LC Line ID')
    shipment_pro_line_id = fields.Integer(string='Shipment Line ID')











