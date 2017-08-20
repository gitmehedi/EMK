from openerp import models, fields
import datetime


MAX_ATTEMPT_TO_SUCCESS = 5


class AttendanceErrorDataProcessor(models.Model):
    _name = 'hr.attendance.error.data.temp'


    def doErrorToSuccess(self):

        hr_employee_pool = self.env['hr.employee']

        hr_att_error_pool = self.env['hr.attendance.import.error']
        errorDataList = hr_att_error_pool.search([('attempt_to_success', '<=', MAX_ATTEMPT_TO_SUCCESS),
                                                  ('import_id', '=', None)], order='id asc')
        for row in errorDataList:
            if row.employee_code:
                emp = hr_employee_pool.search([('device_employee_acc', '=', row.employee_code)], limit=1)
                if emp:
                    self.processErrorData(row, emp.id)
                    row.unlink()
                else:
                    row.write({'attempt_to_success': row.attempt_to_success + 1})

            else:
                row.write({'attempt_to_success': row.attempt_to_success + 1})

    def processErrorData(self, row, employeeId):

        hr_att_pool = self.env['hr.attendance']

        if row.check_in:
            preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                             ('check_out', '!=', False)], limit=1, order='check_out asc')

            if preAttData and preAttData.check_in is False:
                chk_out = self.getDateTimeFromStr(preAttData.check_out)
                durationInHour = (self.getDateTimeFromStr(chk_out) - row.check_in).total_seconds() / 60 / 60
                if durationInHour <= 15 and durationInHour >= 0:
                    preAttData.write({'check_in': self.getDateTimeFromStr(row.check_in),
                                      'worked_hours': durationInHour,
                                      'write_date': datetime.datetime.now(),
                                      'has_error': False,
                                      'operating_unit_id': row.operating_unit_id})
                else:
                    self.createDataFromError(row, employeeId, hr_att_pool)
            else:
                self.createDataFromError(row, employeeId, hr_att_pool)
            # self.createDataFromError(row, employeeId, hr_att_pool)
        elif row.check_out:

            preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                             ('check_in', '!=', False)], limit=1, order='check_in desc')

            if preAttData and preAttData.check_out is False:
                chk_in = self.getDateTimeFromStr(preAttData.check_in)
                durationInHour = (self.getDateTimeFromStr(row.check_out) - chk_in).total_seconds() / 60 / 60
                if durationInHour <= 15 and durationInHour >= 0:
                    preAttData.write({'check_out': self.getDateTimeFromStr(row.check_out),
                                      'worked_hours': durationInHour,
                                      'write_date': datetime.datetime.now(),
                                      'has_error': False,
                                      'operating_unit_id': row.operating_unit_id})
                else:
                    self.createDataFromError(row, employeeId, hr_att_pool)
            else:
                self.createDataFromError(row, employeeId, hr_att_pool)

    def createDataFromError(self, row, employeeId, hr_att_pool):

        if row.check_in:
            create_vals = {'employee_id': employeeId,
                           'check_in': self.getDateTimeFromStr(row.check_in),
                           'create_date': datetime.datetime.now(),
                           'write_date': datetime.datetime.now(),
                           'has_error': True,
                           'manual_attendance_request': False,
                           'is_system_generated': True,
                           'operating_unit_id': row.operating_unit_id}
        else:
            create_vals = {'employee_id': employeeId,
                           'check_in': None,
                           'check_out': self.getDateTimeFromStr(row.check_out),
                           'create_date': datetime.datetime.now(),
                           'write_date': datetime.datetime.now(),
                           'has_error': True,
                           'manual_attendance_request': False,
                           'is_system_generated': True,
                           'operating_unit_id': row.operating_unit_id}

        res = hr_att_pool.create(create_vals)

    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None

    def setDutyDate(self, operating_unit_id):
        hr_att_pool = self.env['hr.attendance']
        att_list = hr_att_pool.search([('attempt_set_duty_date', '<=', MAX_ATTEMPT_TO_SUCCESS),
                                       ('duty_date', '=', None),
                                       ('operating_unit_id', '=', operating_unit_id[0].id)], order='employee_id asc',limit=1000)

        print datetime.datetime.now()

