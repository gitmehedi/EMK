import datetime

from odoo import models, fields, _


class PosProductReturnWizard(models.Model):
    _name = 'pos.product.return.wizard'

    product_ids = fields.Many2many('product.product', string='Products', required=True)

    def return_products(self, context=None):
        order_line = self.env[context['active_model']].lines
        pos_order = self.env[context['active_model']].search([('id', '=', context['active_id'])])
        pos_products = [val.product_id.id for val in pos_order.lines]

        for record in self.product_ids:
            if record.id in pos_products:
                unlink = pos_order.lines.search([('product_id', '=', record.id), ('order_id', '=', pos_order.id)])
                unlink.unlink()
            else:
                rec = {}
                rec['name'] = record.name
                rec['product_id'] = record.id
                rec['company_id'] = record.company_id.id
                rec['order_id'] = pos_order.id
                rec['qty'] = 1
                rec['price_unit'] = record.list_price if record else record.list_price
                order_line.create(rec)
                pos_order.write({'date_order': datetime.datetime.today()})

        return {
            'name': _('Return Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': pos_order.id,
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
    #
    # def get_discount_price(self, ins, record):
    #     for rec in ins.lines:
    #         if rec.product_id.product_tmpl_id.id == record.product_tmpl_id.id:
    #             return rec.discount
