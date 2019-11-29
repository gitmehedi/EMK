from odoo import api, fields, models, tools, _
# from odoo.exceptions import ValidationError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    init_pf = fields.Float("Initial Provident Fund")
    pf_amount = fields.Float("PF Amount")
    pf_lines = fields.One2many('hr.employee.pf.line', 'employee_id', string='PF Lines')


class EmployeePFLine(models.Model):
    _name = 'hr.employee.pf.line'

    name = fields.Char("Narration")
    amount = fields.Float("Amount")


class InheritHRPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()

        pf_line = self.env('hr.employee.pf.line')
        for line in self.line_ids:
            if line.code == 'EPMF':
                vals = {
                    'name': self.name,
                    'amount': abs(line.total)
                }

        return res