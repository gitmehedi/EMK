from odoo import api, fields, models

class HRJob(models.Model):
    _inherit = 'hr.job'

    department_ids = fields.Many2many('hr.department','department_job_rel', 'department_id', 'job_id', string='Departments')