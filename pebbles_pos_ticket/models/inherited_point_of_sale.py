from openerp import api, fields, models


class InheritedPointOfSale(models.Model):
    _inherit = 'pos.category'

    code = fields.Char(string='Code', size=20)


class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'pos.order'

    total_order_amount = fields.Float(string='Total Amount', default="0.0")
    discount_type = fields.Char(string='Discount Type')
    percent_discount = fields.Text(string='Percent Discount')
    cal_discount_amount = fields.Float(string='Discount Amount', default="0.0")

    def _order_fields(self, cr, uid, ui_order, context=None):
        return {
            'name': ui_order['name'],
            'user_id': ui_order['user_id'] or False,
            'session_id': ui_order['pos_session_id'],
            'lines': ui_order['lines'],
            'pos_reference': ui_order['name'],
            'partner_id': ui_order['partner_id'] or False,
            # 			'total_order_amount':ui_order['amount_total'],
            'total_order_amount': ui_order['total_order_amount'],
            'cal_discount_amount': ui_order['cal_discount_amount'],
            #'discount_type': ui_order['discount_type'],
            #'percent_discount': ui_order['percent_discount'],
        }

