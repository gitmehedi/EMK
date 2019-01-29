from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'


    """ All functions """
    @api.constrains('name')
    def _check_unique_name(self):
        if self.name:
            name = self.env['res.partner'].search([('name', '=ilike', self.name)])
            if self.supplier == True:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Vendor Name must be unique!')
            elif self.customer == True:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Customer Name must be unique!')
            else:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Name must be unique!')
