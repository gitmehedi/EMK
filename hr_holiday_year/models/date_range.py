from odoo import models, fields, api


class DateRange(models.Model):
    _inherit = "date.range"

    current = fields.Boolean(string='Is Current?', default=False)

    @api.onchange('date_start', 'date_end')
    def onchange_date(self):
        current_date = fields.Datetime.now()
        if current_date >= self.date_start and current_date <= self.date_end:
            self.current = True
        else:
            self.current = False

    @api.one
    def name_get(self):
        if self.name and self.date_start and self.date_end:
            frmt = '%m/%d/%Y'
            start = fields.Datetime.from_string(self.date_start).strftime(frmt)
            end = fields.Datetime.from_string(self.date_end).strftime(frmt)
            name = '%s [%s - %s]' % (self.name, start, end)
        return (self.id, name)
