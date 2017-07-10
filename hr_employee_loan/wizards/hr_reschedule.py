from openerp import models, fields, api


class HrLoanRescheduleWizard(models.TransientModel):
    _name = 'hr.loan.reschedule.wizard'

    remaining_amount = fields.Float(string="Remaining Loan", compute='hr_employee_loan._compute_loan_amount_with_payslip')
    new_installment_amount = fields.Integer(size=100, string=' New Installment Amount', required=True)
    new_repayment_date = fields.Date('New Repayment Date',required=True)

