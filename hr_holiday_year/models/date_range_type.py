from odoo import models, fields


class DateRangeType(models.Model):
    _inherit = "date.range.type"

    holiday_year = fields.Boolean(string='Is Holiday Year?', default=False)
    holiday_month = fields.Boolean(string='Is Holiday Month?', default=False)
