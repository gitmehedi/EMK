from openerp import api, fields, models

class GbsHrAttendanceDurationCalc(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_hr_att_dur'
    
    @api.model
    def render_html(self, docids, data=None):
        hr_att_pool = self.env['hr.attendance'].search([])

        query = """SELECT check_in,check_out FROM hr_attendance
                                               WHERE
                                               check_in > %s
                                               GROUP BY employee_id"""
        self._cr.execute(query, tuple([employee_id, str_date]))
        result = self._cr.fetchall()


        docargs = {
            'docs': hr_att_pool,
        }

        return self.env['report'].render('gbs_hr_attendance_report.report_hr_att_dur', docargs)
