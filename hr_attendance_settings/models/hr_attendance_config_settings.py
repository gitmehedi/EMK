from odoo import api,fields, models

class HRAttendanceConfigSettings(models.TransientModel):
    _name = 'hr.attendance.config.settings'

    late_salary_deduction_rule = fields.Char(size=2)

    @api.one
    def execute(self):
        vals = {'late_salary_deduction_rule': self.late_salary_deduction_rule}
        return self.create(vals)