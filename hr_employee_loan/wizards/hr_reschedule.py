from openerp import models, fields, api


class HrLoanRescheduleWizard(models.TransientModel):
    _name = 'hr.loan.reschedule.wizard'

    @api.multi
    def _get_remaining_amount(self):
        return self._context['remaining_amount']

    remaining_amount = fields.Integer(string="Remaining Loan",default =_get_remaining_amount)
    new_installment_amount = fields.Integer(size=100, string=' New Installment Amount', required=True)
    new_repayment_date = fields.Date('New Repayment Date',required=True)

    @api.multi
    def genarate_reschudle(self):
        print "-----------"
