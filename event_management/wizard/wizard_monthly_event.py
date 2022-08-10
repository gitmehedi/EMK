from odoo import _, api, models, fields


class WizardMonthlyEvent(models.TransientModel):
    _name = "wizard.monthly.report"

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', default=fields.Date.today, required=True)
    room_id = fields.Many2one('event.room', string='Event Room')

    @api.multi
    def process_report(self):
        data = {}
        data['date_from'] = self.start_date
        data['date_to'] = self.end_date

        if 'pdf' in self._context:
            return self.env['report'].get_action(self, 'event_management.report_event_monthly', data=data)

        if 'xlsx' in self._context:
            return self.env['report'].get_action(self, report_name='event_management.monthly_event_xlsx',data=data)






