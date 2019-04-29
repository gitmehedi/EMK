# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from dateutil.rrule import (rrule,
                            YEARLY,
                            MONTHLY,
                            WEEKLY,
                            DAILY)
from dateutil.relativedelta import relativedelta


class DateRangeGenerator(models.TransientModel):
    _inherit = 'date.range.generator'

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    name_prefix = fields.Char('Period Name Prefix')
    date_start = fields.Date(strint='Start Date')
    type_id = fields.Many2one(string='Type')
    unit_of_time = fields.Selection([
        (YEARLY, 'Years'),
        (MONTHLY, 'Months'),
        (WEEKLY, 'Weeks'),
        (DAILY, 'Days')])
    duration_count = fields.Integer('Duration')
    count = fields.Integer(string="Number of Ranges to Generate")
