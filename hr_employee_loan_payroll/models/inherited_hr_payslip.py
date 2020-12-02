from odoo import api, fields, models


class InheritedHrPayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    remaining_loan = fields.Float(string='Remaining Loan', default=0.00, required=True)

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:

            emp_loan = self.env['hr.employee.loan'].search([('employee_id.id', '=', self.employee_id.id),
                                                            ('state', '=', 'disbursed')])
            loan_amt = 0
            for loan in emp_loan:
                loan_amt += loan.remaining_loan_amount or 0.00

            # if emp_loan:
            self.remaining_loan = loan_amt

            self.input_line_ids = 0
            super(InheritedHrPayslip, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            loan_data = self.env['hr.employee.loan.line'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('schedule_date', '>=', self.date_from),
                                                                  ('schedule_date', '<=', self.date_to),
                                                                  ('state', '=', 'pending')])

            """
            Loan Amount
            """
            line_amt = 0
            for line in loan_data:
                if line.parent_id.state == 'disbursed':
                    line_amt += line.installment
            if self.contract_id.id:
                other_line_ids += other_line_ids.new({
                    'name': 'Current Loan',
                    'code': "LOAN",
                    'amount': line_amt,
                    'contract_id': self.contract_id.id,
                })
                self.input_line_ids = other_line_ids

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedHrPayslip, self).action_payslip_done()
        loan_data = self.env['hr.employee.loan.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('schedule_date', '>=', self.date_from),
                                                              ('schedule_date', '<=', self.date_to),
                                                              ('state', '=', 'pending')])
        for line_state in loan_data:
            if self.contract_id.id and line_state.parent_id.state == 'disbursed':
                line_state.write({'state': 'done'})
                values = {}
                if line_state.parent_id.check_pending_installment() == True:
                    values['state'] = 'closed'

                line_state.parent_id.write(values)

        return res
