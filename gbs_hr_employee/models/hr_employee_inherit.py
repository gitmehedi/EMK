from odoo import api, fields, models
from odoo.exceptions import UserError

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    department_id = fields.Many2one('hr.department', string='Department', required=True)
    tin_req = fields.Boolean(string='TIN Applicable')
    tin = fields.Char(string='TIN')

    employee_sequence = fields.Integer("Employee Sequence")
    total_pf = fields.Float(compute='_compute_total_pf', string='Total PF')
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',
                                      domain="[]",
                                      help='Employee bank salary account', groups='hr.group_hr_user')

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        bank_account_id = vals['bank_account_id']
        if bank_account_id:
            hr_employee = self.env['hr.employee'].search([('bank_account_id', '=', bank_account_id), ('id', '!=', res.id)])
            if hr_employee:
                raise UserError('Bank account already assigned')
            
        return res
            
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if 'bank_account_id' in vals:
            bank_account_id = vals.get('bank_account_id')
            hr_employee = self.env['hr.employee'].search(
                [('bank_account_id', '=', bank_account_id), ('id', '!=', self.id)])
            if hr_employee:
                raise UserError('Bank account already assigned')
        return res

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
                if rec.code == 'EPMF' and rec.slip_id.state == 'done':
                    self.total_pf += abs(rec.total)



