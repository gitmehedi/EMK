from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('default_code')
    def _check_default_code(self):
        if self.default_code:
            code = self.env['product.template'].search([('default_code', '=', self.default_code)])
            if len(code) > 1:
                raise ValidationError(" Internal Reference must be unique!")
