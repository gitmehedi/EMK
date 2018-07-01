from odoo import api, models, fields


class TagSaleOrderWizard(models.TransientModel):
    _name = 'tag.sale.order.wizard'
    _description = 'Tag Sale Order'

    so_id = fields.Many2one('sale.order', string='Select Sale Order', required=True,
                            domain="[('pi_id', '=', False), ('state', '=', 'done'), ('credit_sales_or_lc', '=','lc_sales')]")


    def tag_sale_order(self):
        pi_obj = self.env['proforma.invoice'].browse([self._context['active_id']])
        pi_obj.write({'so_ids': self.so_id})
        self.so_id.write({'pi_id':pi_obj.id})



