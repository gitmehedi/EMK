from odoo import models, fields, api, _, exceptions


class DateRangeType(models.Model):
    _inherit = "date.range.type"

    holiday_year = fields.Boolean(string='Is Holiday year?', default=False)

    holiday_month = fields.Boolean(string='Is Holiday month?', default=False)