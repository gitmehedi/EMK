from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    service_charge = fields.Float(string='Service Charge')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    service_charge = fields.Float(string='Service Charge')
    amount_tax = fields.Float(compute='_compute_amount_all', string='VAT', digits=0)


