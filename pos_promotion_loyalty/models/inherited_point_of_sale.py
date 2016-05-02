from openerp import api, fields, models


class InheritedPointOfSale(models.Model):
    _inherit = 'pos.category'

    loyalty_point = fields.Integer(string='Loyalty Point')
    code = fields.Char(string='Code', size=20)


class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'pos.order'

    total_order_amount = fields.Float(string='Total Amount', default="0.0")
    discount_type = fields.Char(string='Discount Type')
    percent_discount = fields.Text(string='Percent Discount')
    cal_discount_amount = fields.Float(string='Discount Amount', default="0.0")

    # def create(self, cr, uid, values, context=None):
    #     if values.get('session_id'):
    #         # set name based on the sequence specified on the config
    #         session = self.pool['pos.session'].browse(cr, uid, values['session_id'], context=context)
    #         values['name'] = session.config_id.sequence_id._next()
    #     else:
    #         # fallback on any pos.order sequence
    #         values['name'] = self.pool.get('ir.sequence').get_id(cr, uid, 'pos.order', 'code', context=context)
    #
    #     return super(InheritedPurchaseOrderLine, self).create(cr, uid, values, context=context)

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
