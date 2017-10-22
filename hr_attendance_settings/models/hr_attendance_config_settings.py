from odoo import api,fields, models

class HRAttendanceConfigSettings(models.TransientModel):
    _name = 'hr.attendance.config.settings'

    late_salary_deduction_rule = fields.Char(size=2,string = 'Allow rule, if any employee late in 3 days his/her salary will deduct.')

    @api.model
    def execute(self):
        return


