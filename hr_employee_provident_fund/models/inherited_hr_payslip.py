from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    @api.depends('init_pf')
    def _compute_total_pf(self):
        for emp in self:
            pfa = emp.init_pf
            for line in emp.pf_lines:
                pfa += line.amount
            emp.total_pf = pfa

    init_pf = fields.Float("Initial Provident Fund")
    total_pf = fields.Float(compute='_compute_total_pf', string='Total PF', store=True)

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