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


    # @api.one
    # def _order_fields(self):
    #     return {
    #         'name': self.name,
    #         'user_id': self.user_id.id,
    #         'session_id': self.session_id.id,
    #         'lines': self.lines,
    #         'pos_reference': self.pos_reference,
    #         'partner_id': self.partner_id.id,
    #         'total_order_amount': self.total_order_amount,
    #         'cal_discount_amount': self.cal_discount_amount,
    #     }
