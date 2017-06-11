from openerp import api, fields, models

class DailyAttendance(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_daily_attendance'

    @api.model
    def render_html(self, docids, data=None):
        hr_att_pool = self.env['hr.attendance'].search([])
        docargs = {
            'docs': hr_att_pool,
        }
        return self.env['report'].render('gbs_hr_attendance_report.report_daily_attendance', docargs)

