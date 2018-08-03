from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit='res.partner'


    """ Relational Fields """
    commission_ids = fields.One2many('customer.commission', 'customer_id', string='Commission', readonly=True)
