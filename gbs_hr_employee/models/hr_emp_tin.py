from odoo import api, fields, models, tools, _

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    department_id = fields.Many2one('hr.department', string='Department',required=True)
    tin_req= fields.Boolean(string='TIN Applicable')
    tin = fields.Char(string = 'TIN')
