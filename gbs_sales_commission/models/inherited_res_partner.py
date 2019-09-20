from odoo import fields, api, models
from odoo.exceptions import ValidationError


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    """ Relational Fields """
    commission_ids = fields.One2many('customer.commission', 'customer_id', string='Commission', readonly=True)

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:

            sql = """SELECT * FROM res_partner WHERE name =%s"""
            self._cr.execute(sql, (self.name.strip(),))  # Never remove the comma after the parameter
            partners = self._cr.fetchall()

            if len(partners) > 1:
                raise ValidationError('Customer name already in use')
