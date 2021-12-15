import time
import re
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import dateutil.parser
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


class AppointmentWizard(models.TransientModel):
    _name = 'appointment.wizard'

    appointment_date = fields.Date('Appointment Date', required=True, track_visibility="onchange")

    @api.one
    @api.constrains('appointment_date')
    def validate_appointment_date(self):
        if self.appointment_date:
            app_date = datetime.strptime(self.appointment_date, '%Y-%m-%d')
            curr_date = dateutil.parser.parse(fields.Date.today())
            if app_date < curr_date:
                raise ValidationError(_("Appointment date cannot be past date from current date"))

    def act_change_date(self):
        id = self._context['active_id']

        record = self.env['appointment.appointment'].search([('id', '=', id)])

        if record:
            record.write({'appointment_date': self.appointment_date})




