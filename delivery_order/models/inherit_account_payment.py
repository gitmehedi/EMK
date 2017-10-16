from odoo import fields, models

class InheritAccountPayment(models.Model):
    _inherit='account.payment'

    sale_order_id = fields.Many2one('sale.order',string='Sale Order')
    is_this_payment_checked = fields.Boolean(string='Is This Payment checked with SO', default=False)
    my_menu_check = fields.Boolean(string='Check')

    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
        ('transfer','Internal Transfer')
    ], string='Payment Type', default='inbound')

