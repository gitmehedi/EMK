from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class DeliveryScheduleEntryLine(models.Model):
    _name = 'delivery.schedules.line'
    _description = 'Delivery Schedule line'

    partner_id = fields.Many2one('res.partner', 'Customer',domain="([('customer','=','True')])")
    product_id = fields.Many2one('product.product','Products',required=True)
    quantity = fields.Float(string="Ordered Qty",default=1.0, required=True)
    uom_id = fields.Many2one('product.uom', string="UoM",required=True)
    pack_type = fields.Many2one('product.packaging.mode', string="Packing")
    deli_address = fields.Text('Delivery Address')
    parent_id = fields.Many2one('delivery.schedules')
    remarks = fields.Text('Remarks')
    state = fields.Selection([
        ('draft', "Draft"),
        ('approve', "Confirm"),
    ], default='draft')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            product_obj = self.env['product.template'].search([('id', '=', self.product_id.id)])
            if product_obj:
                self.uom_id = product_obj.uom_id.id


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.parent_id:
            customer_obj = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
            if customer_obj:
                self.deli_address = customer_obj.street

    @api.constrains('quantity')
    def check_credit_days(self):
        if self.quantity < 0.00:
            raise ValidationError('Days can not be negative')