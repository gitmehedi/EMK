from odoo import models, fields, api, _, exceptions


class DateRange(models.Model):
    _inherit = "date.range"

    current = fields.Boolean(string='Is Current?', default=False)

    @api.onchange('date_start','date_end')
    def onchange_date(self):
        current_date = fields.Datetime.now()
        if current_date >= self.date_start and current_date<= self.date_end:
            self.current = True
        else:
            self.current = False