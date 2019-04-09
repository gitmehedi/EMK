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


    late_salary_deduction_rule = fields.Integer(size= 4, default=_get_default)


    def _get_time_duration(self):
        query = """select time_duration from hr_attendance_config_settings order by id desc limit 1"""
        self._cr.execute(query, tuple([]))
        param_value = self._cr.fetchone()
        if param_value:
            return param_value[0]

    time_duration = fields.Integer(size= 5, default=_get_time_duration)

    @api.multi
    def _get_server_url(self):
        query = """select server_url from hr_attendance_config_settings order by id desc limit 1"""
        self._cr.execute(query, tuple([]))
        url_value = self._cr.fetchone()
        if url_value:
            return url_value[0]

    server_url = fields.Char(default=_get_server_url)

    @api.model
    def create(self,vals):
        config_id = super(HRAttendanceConfigSettings, self).create( vals)
        return config_id