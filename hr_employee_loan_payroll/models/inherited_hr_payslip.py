from odoo import api, fields, models, tools, _


class InheritedHrMobilePayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrMobilePayslip, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            loan_data = self.env['hr.employee.loan.line'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('schedule_date', '>=', self.date_from),
                                                                  ('schedule_date', '<=', self.date_to),
                                                                  ('state', '=', 'pending')], limit=1)

            """
            Meal Bills
            """
            if loan_data and self.contract_id.id:
                other_line_ids += other_line_ids.new({
                    'name': 'Current Loan',
                    'code': "LOAN",
                    'amount': loan_data.installment,
                    'contract_id': self.contract_id.id,
                })
            self.input_line_ids = other_line_ids

    @api.multi
    def action_payslip_done_with_loan(self):
        self.action_payslip_done()
        loan_data = self.env['hr.employee.loan.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('schedule_date', '>=', self.date_from),
                                                              ('schedule_date', '<=', self.date_to),
                                                              ('state', '=', 'pending')], limit=1)
        if loan_data:
            loan_data.write({'state': 'done'})
            loan_data.parent_id.write({'remaining_loan_amount': loan_data.parent_id.remaining_loan_amount - loan_data.installment})
            return True


