from odoo import api, fields, models

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    department_id = fields.Many2one('hr.department', string='Department', required=True)
    tin_req = fields.Boolean(string='TIN Applicable')
    tin = fields.Char(string='TIN')

    employee_sequence = fields.Integer("Employee Sequence")
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.job_id:
                name = "%s [%s]" % (name,record.job_id.name_get()[0][1])
            result.append((record.id, name))
        return result

