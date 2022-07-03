from odoo import api, fields, models, tools, _


class InheritedHrPayrollAbsentPayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedHrPayrollAbsentPayslip, self).action_payslip_done()

        hmpa_ids = []
        for li in self.input_line_ids:
            if li.code == 'HMPA':
                hmpa_ids.append(int(li.ref))

        hmpa_data = self.env['hr.employee.payroll.absence.line'].browse(hmpa_ids)
        hmpa_data.write({'state': 'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrPayrollAbsentPayslip, self).onchange_employee()

            line_ids = self.input_line_ids
            lines = self.env['hr.employee.payroll.absence.line'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'applied')])

            for line in lines:
                line_ids += line_ids.new({
                    'name': 'Employee Payroll Absent',
                    'code': "HMPA",
                    'amount': line.days,
                    'contract_id': self.contract_id.id,
                    'ref': line.id
                })
            self.input_line_ids = line_ids
