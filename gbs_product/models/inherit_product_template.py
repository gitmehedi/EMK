from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cost_center_id = fields.Many2one('account.cost.center', string='Cost Center')
    receive_over_ok = fields.Boolean(string='Can be Received Over', default=False, track_visibility='onchange')

    @api.constrains('default_code')
    def _check_default_code(self):
        if self.default_code:
            code = self.env['product.template'].search([('default_code', '=', self.default_code)])
            if len(code) > 1:
                raise ValidationError(" Internal Reference must be unique!")


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(track_visibility='onchange')
