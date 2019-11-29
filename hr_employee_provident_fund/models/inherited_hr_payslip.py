from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    init_pf = fields.Float("Initial Provident Fund")
    pf_amount = fields.Float("PF Amount")

    # Relational fields
    pf_lines = fields.One2many('hr.employee.pf.line', 'employee_id', string='PF Lines', readonly="True")


class EmployeePFLine(models.Model):
    _name = 'hr.employee.pf.line'

    name = fields.Char("Narration")
    amount = fields.Float("Amount")

    # Relational fields
    employee_id = fields.Many2one('hr.employee', string="Employee")

    @api.multi
    def unlink(self):
        raise UserError(_('You can not delete this.'))


class InheritHRPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()

        pf_line = self.env['hr.employee.pf.line']
        for line in self.line_ids:
            if line.code == 'EPMF':
                vals = {
                    'name': self.name,
                    'amount': abs(line.total),
                    'employee_id': self.employee_id.id
                }

                pf_line.create(vals)

        return res