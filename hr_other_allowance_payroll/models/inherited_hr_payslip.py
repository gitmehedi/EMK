from odoo import api, fields, models, tools, _

class InheritHROthersPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')

    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHROthersPayslipInput, self).action_payslip_done()

        other_ids = []
        for li in self.input_line_ids:
            if li.code == 'OAS':
                other_ids.append(int(li.ref))

        other_line_pool = self.env['hr.other.allowance.line']
        other_data = other_line_pool.browse(other_ids)
        other_data.write({'state':'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = 0
            super(InheritHRPayslipInput, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            other_datas = self.env['hr.other.allowance.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state','=','approved')])

            """
            Other Allowance Bills
            """
            for other_data in other_datas:
                other_line_ids += other_line_ids.new({
                    'name': 'Other Allowance',
                    'code': "OAS",
                    'amount': other_data.other_allowance_amount,
                    'contract_id': self.contract_id.id,
                    'ref': other_data.id,
                })

            self.input_line_ids = other_line_ids
