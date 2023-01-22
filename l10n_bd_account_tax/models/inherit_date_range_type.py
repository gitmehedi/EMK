from odoo import models, fields, api, _, exceptions


class DateRangeType(models.Model):
    _inherit = "date.range.type"

    tds_year = fields.Boolean(string="Is TDS Year?", default=False)
