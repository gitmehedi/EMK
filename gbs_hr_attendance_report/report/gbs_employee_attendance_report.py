from odoo import api, models, fields, _
from odoo import exceptions

class EmployeeAttendanceReport(models.AbstractModel):
    _name = "report.gbs_hr_attendance_report.gbs_employee_attendance_doc"

    @api.model
    def render_html(self, docids, data=None):

        process_date_from = "'" + str(data['date_from']) + " 00:00:00" + "'"
        process_date_to = "'" + str(data['date_to']) + " 23:59:59" + "'"

        cio_list = self.filter_data(data['employee_id'], process_date_from, process_date_to)

        try:
            cio_data = self.proces_check_in_out_data(cio_list)
        except IndexError:
            raise exceptions.Warning(
                       _('There is no attendance data for this employee')
                     )

        docargs = {
            'data': data,
            'cio_data': cio_data
        }
        return self.env['report'].render('gbs_hr_attendance_report.gbs_employee_attendance_doc', docargs)

    def proces_check_in_out_data(self, cio_list):
        cio_data = {}
        seq = 1
        for data in cio_list:
            cio_data[seq] = {}
            rec = cio_data[seq]
            rec['check_in'] = str(data[0]) if data[0] else ''
            rec['check_out'] = str(data[1]) if data[1] else ''
            rec['duty_date'] = str(data[2]) if data[2] else ''
            seq += 1
        return cio_data

    def filter_data(self, emo_id, from_date, to_date):

        self._cr.execute('''
        SELECT check_in + INTERVAL '6h',
               check_out + INTERVAL '6h',
               duty_date
        FROM hr_attendance
        WHERE employee_id = %s
              AND ((check_in BETWEEN %s AND %s)
              OR (check_out BETWEEN %s AND %s))
        ORDER BY check_in
        ''' % (emo_id, from_date, to_date, from_date, to_date))
        result = self._cr.fetchall()

        return result
