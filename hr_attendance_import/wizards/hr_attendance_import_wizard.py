try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64
import csv
import time
from datetime import datetime
from sys import exc_info
from traceback import format_exception

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.loglevels import ustr

import logging
_logger = logging.getLogger(__name__)

from openerp.exceptions import ValidationError,Warning

from datetime import timedelta


class HrAttendanceImportWizard(models.TransientModel):
    _name = 'hr.attendance.import.wizard'

    aml_data = fields.Binary(string='File')
    aml_fname = fields.Char(string='Filename')
    note = fields.Text('Log')

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self._default_operating_unit(), readonly=True)
    attendance_id = fields.Many2one(
        'hr.attendance.import',
        default=lambda self: self._default_attendance_id(),
        string='Attendance'
    )

    @api.multi
    def attendance_import(self):
        if self and self.aml_data:
            try:
                values = []
                values = self.env['gbs.read.excel.utility'].read_xls_book(self.aml_data)
                vals = {
                    'attendance_id': self.attendance_id.id,
                }
                if self.save_line_data(values):
                    message_id = self.env['attendance.success.wizard'].create({'message': _(
                        "Attendance Imported Successfully!")
                    })
                    return {
                        'name': _('Success'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'attendance.success.wizard',
                        'context': vals,
                        'res_id': message_id.id,
                        'target': 'new'
                    }
                else:
                    message_id = self.env['attendance.success.wizard'].create({'message': _(
                        "Attendance Imported Failed!")
                    })
                    return {
                        'name': _('Failure'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'attendance.success.wizard',
                        'context': vals,
                        'res_id': message_id.id,
                        'target': 'new'
                    }

            except Exception as e:
                raise UserError(_("Attendance Import Failed!" + ustr(e)))

    def _default_attendance_id(self):
        attendance_id = self.env['hr.attendance.import'].browse(self.env.context.get('active_id'))
        return attendance_id

    def _default_operating_unit(self):
        attendance_id = self.env['hr.attendance.import'].browse(self.env.context.get('active_id'))
        return attendance_id.operating_unit_id.id
    def save_line_data(self, values):

        sorted_multi_list = sorted(values, key=lambda x: x[3])

        attendance_import_line_obj = self.env['hr.attendance.import.line']
        attendance_import_error_obj = self.env['hr.attendance.import.error']
        ReportUtility = self.env['report.utility']
        errors = []

        # delete exiting import data and error data
        import_data = self.env['hr.attendance.import.line'].search([('import_id', '=', self.attendance_id.id)])
        import_data.unlink()

        error_data = self.env['hr.attendance.import.error'].search([('import_id', '=', self.attendance_id.id)])
        error_data.unlink()

        for val in sorted_multi_list:
            if val[1] == '0':
                raise UserError('''You cannot upload employee attendance which contains '0' as AC No!''')

            employee_obj = self.env['hr.employee'].search(
                [('device_employee_acc', '=', int(val[1])), ('operating_unit_id', '=', self.operating_unit_id.id)])

            if len(employee_obj) > 1:
                error_msg = 'Uploading Failed ! Below Employees have same account number!'
                for emp in employee_obj:
                    error_msg = error_msg + "\n" + str(emp.name) + ' AC NO: ' + str(emp.device_employee_acc)

                raise UserError(error_msg)
            # date_time_check_in = datetime.strptime(str(val[3]), '%d/%m/%Y %H:%M:%S') - timedelta(hours=6)
            date_time_check_in = datetime.strptime(str(val[3]), '%d/%m/%Y %H:%M:%S') - timedelta(hours=6)
            # check_in = ReportUtility.get_date_time_from_string(str(date_time_check_in))
            check_in = date_time_check_in
            date_time_check_out = datetime.strptime(str(val[4]), '%d/%m/%Y %H:%M:%S') - timedelta(hours=6)
            # check_out = ReportUtility.get_date_time_from_string(str(date_time_check_out))
            check_out = date_time_check_out

            # time_diff = date_time_check_out - date_time_check_in
            time_diff = check_out - check_in
            diff_in_hours = time_diff.total_seconds() / 3600

            if employee_obj and diff_in_hours <= 14:
                attendance_import_line_obj.create({
                    'import_id': self.attendance_id.id,
                    'employee_id': employee_obj.id,
                    'acc_no': int(val[1]),
                    'operating_unit_id': self.operating_unit_id.id,
                    'company_id': self.company_id.id,
                    'check_in': check_in,
                    'check_out': check_out
                })
            else:
                # date_time_check_in = datetime.strptime(str(val[3]), '%d/%m/%Y %H:%M:%S') + timedelta(hours=6)
                # check_in = ReportUtility.get_date_time_from_string(str(date_time_check_in))
                # date_time_check_out = datetime.strptime(str(val[4]), '%d/%m/%Y %H:%M:%S') + timedelta(hours=6)
                # check_out = ReportUtility.get_date_time_from_string(str(date_time_check_out))

                attendance_import_error_obj.create({
                    'import_id': self.attendance_id.id,
                    'employee_id': employee_obj.id,
                    'acc_no': int(val[1]),
                    'check_in': check_in,
                    'check_out': check_out
                })

        return True


