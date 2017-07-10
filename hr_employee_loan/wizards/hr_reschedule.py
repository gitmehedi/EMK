from openerp import models, fields, api

class HrLoanRescheduleWizard(models.TransientModel):
    _name = 'hr.loan.reschedule.wizard'

    remaining_loan_amount = fields.Float(string=" New Remaining Loan", digits=(15, 2), compute="_compute_loan_amount_with_payslip")
    new_installment_amount = fields.Integer(size=100, string=' New Installment Amount', required=True)
    new_repayment_date = fields.Date('New Repayment Date',required=True)

