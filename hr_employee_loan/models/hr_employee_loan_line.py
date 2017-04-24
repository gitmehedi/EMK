from openerp import models, fields


class HrLeaveCarryForwardtLine(models.Model):
    _name = 'hr.employee.loan.line'
    _description = 'HR loan line'

    schedule_date = fields.Date(string="Schedule Date")
    installment = fields.Float(size=100, string='Installment Amount', readonly=True)
    num_installment = fields.Integer(string="Number Of Installment")

    """ Relational Fields """
    emp_loan = fields.Many2one('hr.employee.loan')
    parent_id = fields.Many2one('hr.employee.loan', ondelete="cascade")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    state = fields.Selection([
        ('pending', "Pending"),
        ('done', "Done")
    ], default='pending')

