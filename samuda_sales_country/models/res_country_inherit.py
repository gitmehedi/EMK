from odoo import models, fields, api


class ResCountryInherit(models.Model):
    _inherit = 'res.country'

    is_sales_country = fields.Boolean(string='Is Sales Country', default=False)
