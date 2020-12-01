from odoo import models, fields


class HrEmployeeLoantLine(models.Model):
    _name = 'hr.employee.loan.line'
    _description = 'HR loan line'

    emp_loan = fields.Char(string='Code')
    schedule_date = fields.Date(string="Schedule Date")
    installment = fields.Float(size=100, string='Installment Amount', readonly=True)
    num_installment = fields.Integer(string="Installment No")

    """ Relational Fields """
    parent_id = fields.Many2one('hr.employee.loan', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade')

    """ All Selection fields """
    state = fields.Selection([
        ('pending', "Pending"),
        ('done', "Done")
    ], default='pending')
