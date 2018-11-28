from openerp import api, fields, models



class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    mode_of_payment = fields.Char(string='Mode Of Payment')
    delivery = fields.Char(string='Delivery')
    delivery_period = fields.Char(string='Delivery Period')
    warranty = fields.Char(string='Warranty')

    pi_number = fields.Char(string='Order Ref/ PI No')


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    tolerance = fields.Char(string='Tolerance')
