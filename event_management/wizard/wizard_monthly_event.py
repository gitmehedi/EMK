
from odoo import _,api,models,fields


class WizardMonthlyEvent(models.TransientModel):
    _name="wizard.monthly.report"

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    room_id = fields.Many2one('event.room',string='Event Room')


    @api.multi
    def process_report(self):
        data = {}
        data['date_from'] = self.start_date
        data['date_to'] = self.end_date

        return self.env['report'].get_action(self,'event_management.report_event_monthly', data=data)
