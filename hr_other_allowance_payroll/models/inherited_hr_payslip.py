from odoo import api, fields, models, tools, _

class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')

    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslipInput, self).action_payslip_done()

        other_ids = []
        for input in self.input_line_ids:
            if input.code == 'OAS':
                other_ids.append(int(input.ref))

        other_line_pool = self.env['hr.other.allowance.line']
        other_data = other_line_pool.browse(other_ids)
        other_data.write({'state':'adjusted'})

        return res

    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):

        res = super(InheritHRPayslipInput, self).onchange_employee_id(date_from,
                                                                            date_to,
                                                                            employee_id,
                                                                            contract_id)

        if self.employee_id:
            self.input_line_ids = 0
            #super(InheritHRPayslipInput, self).onchange_employee()

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
        return res