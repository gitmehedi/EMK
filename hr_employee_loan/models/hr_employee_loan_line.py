from openerp import models, fields
import datetime
from openerp import api


class HrLeaveCarryForwardtLine(models.Model):
    _name = 'hr.employee.loan.line'
    _description = 'HR loan line'

    emp_loan = fields.Many2one('hr.employee.loan')
    interest_amount = fields.Integer(string="Interest_Amount")
    schedule_date = fields.Datetime(string="Schedule Date")
    installment = fields.Float(size=100, string='Loan Installment',
                                 readonly=True)
    num_installment = fields.Integer(string ="Number Of Installment")

    """ Relational Fields """
    # def _default_employee(self):
    #     return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    parent_id = fields.Many2one(comodel_name='hr.employee.loan')
    employee_id = fields.Many2one('hr.employee', string="Employee")
                                  #default=_default_employee,
                                  # required=True, ondelete='cascade', index=True,
                                  # states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                  #         'approved': [('readonly', True)]})