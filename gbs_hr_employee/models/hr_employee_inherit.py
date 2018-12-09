from odoo import api, fields, models

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    department_id = fields.Many2one('hr.department', string='Department', required=True)
    tin_req = fields.Boolean(string='TIN Applicable')
    tin = fields.Char(string='TIN')

    employee_sequence = fields.Integer("Employee Sequence")
    total_pf = fields.Float(compute='_compute_total_pf', string='Total PF')
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.job_id:
                name = "%s [%s]" % (name,record.job_id.name_get()[0][1])
            result.append((record.id, name))
        return result

    @api.one
    def _compute_total_pf(self):
        for name in self:
            payslip_line = name.suspend_security().env['hr.payslip.line'].search([('employee_id','=',name.id)])
            for rec in payslip_line:
                    if rec.code == 'EPMF':
                        self.total_pf += abs(rec.total)



