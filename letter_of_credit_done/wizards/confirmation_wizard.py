from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Confirmation(models.TransientModel):
    _name = 'lc.done.confirmation.wizard'

    def _default_comment(self):
        return self.env.context.get('message')

    def _default_products(self):

        lc_id = self.env.context.get('lc_id')

        product_line = []
        lc_pro_line = self.env['lc.product.line'].search([('lc_id', '=', lc_id)])

        for obj in lc_pro_line:
            product_qty = obj.product_qty - obj.product_received_qty
            if product_qty > 0:
                product_line.append((0, 0, {'product_id': obj.product_id,
                                            'lc_pro_line_id': obj.id,
                                            'name': obj.name,
                                            'product_qty': obj.product_qty,
                                            'currency_id': obj.currency_id,
                                            'date_planned': obj.date_planned,
                                            'product_uom': obj.product_uom,
                                            'price_unit': obj.price_unit,
                                            'product_received_qty': obj.product_received_qty
                                            }))

        return product_line

    text = fields.Text(default=_default_comment)


    product_lines = fields.One2many('lc.product.line', 'lc_id', string='Product(s)' , default=_default_products, store=False)

    def do_lc_done(self):
        res = self.env.ref('letter_of_credit_done.lc_evaluation_wizard')
        result = {
            'name': _('LC Done'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.evaluation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {"lc_id": self.env.context.get('lc_id')},

        }
        return result