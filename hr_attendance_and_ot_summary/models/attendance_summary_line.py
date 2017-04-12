# sprite class

from openerp import api, models, fields

class AttendanceSummaryLine(models.Model):
    _name = 'hr.attendance.summary.line'

    salary_days = fields.Integer(string='Salary Days', required=True)    #
    present_days = fields.Integer(string='Present Days', required=True)
    late_days_overwrite = fields.Integer(string='Late Days Overwrite')
    leave_days = fields.Integer(string='Leave Days')
    late_hrs = fields.Float(string='Late Hours')
    schedule_ot_hrs = fields.Float(string='Schedule OT Hrs')
    cal_ot_hrs = fields.Float(string='Cal OT Hrs')

    """" Relational Fields """
    att_summary_id = fields.Many2one("hr.attendance.summary", string="Summary", required=True, ondelete='cascade')
    employee_id = fields.Many2one("hr.employee", string='Employee Name', required=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    store=True)

    absent_days = fields.One2many('hr.attendance.absent.day', 'att_summary_line_id', string='Absent Days')
    absent_days_count = fields.Integer(string="Absence Days", compute="_set_absent_days_count")

    late_days = fields.One2many('hr.attendance.late.day', 'att_summary_line_id', string='Late Days')
    late_days_count = fields.Integer(string="Late Days", compute="_set_late_days_count")

    weekend_days = fields.One2many('hr.attendance.weekend.day', 'att_summary_line_id', string='Weekend Days')
    weekend_days_count = fields.Integer(string="Weekend Days", compute="_set_weekend_days_count")

    @api.depends('absent_days')
    def _set_absent_days_count(self):
        for line in self:
            if line.absent_days:
                line.absent_days_count = len(line.absent_days)
            else:
                line.absent_days_count = 0

    @api.depends('late_days')
    def _set_late_days_count(self):
        for line in self:
            if line.late_days:
                line.late_days_count = len(line.late_days)
            else:
                line.late_days_count = 0

    @api.depends('weekend_days')
    def _set_weekend_days_count(self):
        for line in self:
            if line.weekend_days:
                line.weekend_days_count = len(line.weekend_days)
            else:
                line.weekend_days_count = 0

    @api.multi
    def action_regenerate(self):

        print ("Employee ID :", self[0].employee_id)
        empIds = [self.employee_id.id]
        summaryId = self.att_summary_id.id
        attendanceProcess = self.env['hr.attendance.summary.temp']
        attendanceProcess.process(empIds, summaryId)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.attendance.summary',
            'res_model': 'hr.attendance.summary',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': summaryId
        }


class TempAttendanceSummaryLine(object):

    def __init__(self, salary_days=0, present_days=0, late_days_overwrite=0, leave_days=0, late_hrs=0,
                 schedule_ot_hrs=0, cal_ot_hrs=0, employee_id=0, absent_days=None, late_days=None, weekend_days=None):

        self.salary_days = salary_days
        self.present_days = present_days
        self.late_days_overwrite = late_days_overwrite
        self.leave_days = leave_days
        self.late_hrs = late_hrs
        self.schedule_ot_hrs = schedule_ot_hrs
        self.cal_ot_hrs = cal_ot_hrs
        self.employee_id = employee_id
        if absent_days is None:
            self.absent_days = []
        else:
            self.absent_days = absent_days

        if late_days is None:
            self.late_days = []
        else:
            self.late_days = late_days

        if weekend_days is None:
            self.weekend_days = []
        else:
            self.weekend_days = weekend_days