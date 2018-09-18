from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit='res.partner'


    """ Relational Fields """
    commission_ids = fields.One2many('customer.commission', 'customer_id', string='Commission', readonly=True)


    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Customer Name must be unique!')