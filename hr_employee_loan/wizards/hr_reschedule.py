from odoo import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta



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
        ### Remove the Unpaid Schedule
        loan_pool = self.env['hr.employee.loan']
        loan_line_pool = self.env['hr.employee.loan.line']
        loan = loan_pool.browse([self._context['active_id']])
        loan_lines = loan_line_pool.search([('state','!=','done'),
                                            ('parent_id','=',loan.id)])
        loan_lines.unlink()

        ### Generate New Schedule
        loan_amt = self.remaining_amount
        repayment_date = datetime.datetime.strptime(self.new_repayment_date, '%Y-%m-%d')
        installament_amt = self.new_installment_amount
        loan.installment_amount=installament_amt
        i = 1
        while loan_amt > 0:
            vals = {}
            vals['employee_id'] = loan.employee_id.id
            vals['schedule_date'] = repayment_date
            if loan_amt > installament_amt:
                vals['installment'] = installament_amt
            else:
                vals['installment'] = loan_amt
            vals['num_installment'] = i
            vals['parent_id'] = loan.id
            repayment_date = repayment_date + relativedelta(months=1)
            loan.line_ids.create(vals)
            i += 1
            loan_amt -= installament_amt
