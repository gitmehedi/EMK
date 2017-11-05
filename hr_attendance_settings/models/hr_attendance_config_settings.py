from odoo import api,fields, models

class HRAttendanceConfigSettings(models.Model):
    _name = 'hr.attendance.config.settings'
    _inherit = 'res.config.settings'

    @api.multi
    def _get_default(self):
        query = """select late_salary_deduction_rule from hr_attendance_config_settings order by id desc limit 1"""
        self._cr.execute(query, tuple([]))
        deduction_rule_value = self._cr.fetchone()
        if deduction_rule_value:
            return deduction_rule_value[0]


    late_salary_deduction_rule = fields.Integer(size=2,default=_get_default)

    @api.model
    def create(self,vals):
        config_id = super(HRAttendanceConfigSettings, self).create( vals)
        return config_id