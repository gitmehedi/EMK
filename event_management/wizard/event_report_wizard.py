# -*- coding: utf-8 -*-
from datetime import datetime as dt

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EventReportWizard(models.TransientModel):
    _name = 'event.report.wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', default=fields.Date.today, required=True)
    room_id = fields.Many2one('event.room', string='Event Room')

    @api.multi
    def button_export_xlsx(self):
        # start = self.start_date + " 00:00:00"
        # end = self.end_date + " 23:59:59"

        # record = self.env['event.event'].search([('date_begin', '>=', start), ('date_end', '<=', end)])
        # return self.env['report'].get_action(self, 'event_management.report_event_monthly', data=data)
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='event_management.events_xls')
