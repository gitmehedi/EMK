from openerp import models, fields
from openerp import api
from odoo import exceptions, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrAttendance(models.Model):
    _inherit = ['hr.attendance']


    is_system_generated = fields.Boolean(string='Is System Generated', default=False)
    # attendance_server_id will be deprecated after 02-08-2017. operating_unit_id will fill
    #attendance_server_id = fields.Integer(string='Server ID', required=False)
    operating_unit_id = fields.Integer(string='Operating Unit Id', required=False)

    duty_date = fields.Date(string='Duty Date', required=False)
    attempt_set_duty_date = fields.Integer(string='Attempt to set Duty Date', required=False,default=0)
    check_in = fields.Datetime(string="Check In", required=False)

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        return False

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                attendance.worked_hours = delta.total_seconds() / 3600.0

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out >= attendance.check_in:
                raise exceptions.ValidationError(_(
                    "Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                                                     'empl_name': attendance.employee_id.name_related,
                                                     'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self,
                                                      fields.Datetime.from_string(attendance.check_in))), })

    @api.depends('check_in', 'check_out')
    def onchange_attendance_data(self):
        for att in self:
            if (att.check_in is None) or (att.check_out is None) or (att.check_in is False) or (att.check_out is False):
                att.has_error = True

            elif att.check_out < att.check_in:
                att.has_error = True

            else:
                att.has_error = False

class HrEmployee(models.Model):
    _inherit = ['hr.employee']

    device_employee_acc = fields.Integer(string='AC No.')
    is_monitor_attendance=fields.Boolean(string='Monitor Attendance',default=True)
    is_executive = fields.Boolean(string='Executive',default=False)

    _sql_constraints = [
        ('device_employee_acc_uniq', 'unique(device_employee_acc, operating_unit_id)',
         'The Account Number must be unique per Unit!'),
    ]

