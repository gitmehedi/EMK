from odoo import models, fields, api, _, exceptions


class DateRangeType(models.Model):
    _inherit = "date.range.type"

    purchase_year = fields.Boolean(string='Is Purchase year?', default=False)

    purchase_month = fields.Boolean(string='Is Purchase month?', default=False)