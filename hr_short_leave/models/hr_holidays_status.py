from odoo import models, fields, api, SUPERUSER_ID


class HrHolidayStatus(models.Model):
    _inherit = 'hr.holidays.status'

    short_leave_flag = fields.Boolean(string='Allow Short Leave', default=False)
    half_leave_flag = fields.Boolean(string='Allow Half Yearly Leave', default=False)
    compensatory_flag = fields.Boolean(string='Allow Compensatory Leave', default=False)
    number_of_hours = fields.Integer(string='Leave Hours')
    active = fields.Boolean(default=True, string='Status')


class EmployeeLeaves(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    @api.multi
    def _compute_leaves_count(self):
        super(EmployeeLeaves, self)._compute_leaves_count()

    leaves_count = fields.Float('Number of Leaves', compute='_compute_leaves_count', readonly=0)


class HrHoliday(models.Model):
    _inherit = 'hr.holidays'
