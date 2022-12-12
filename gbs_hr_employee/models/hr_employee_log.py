from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_id = fields.Many2one('hr.department', string='Department', required=True, track_visibility='onchange')
    job_id = fields.Many2one('hr.job', string='Job Title', track_visibility='onchange')


class HrJob(models.Model):
    _inherit = "hr.job"

    name = fields.Char(string='Job Title', required=True, index=True, translate=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['hr.job'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError("Job Title must be unique!")


class HrDepartment(models.Model):
    _inherit = "hr.department"

    name = fields.Char(string='Department Name', required=True, track_visibility='onchange')