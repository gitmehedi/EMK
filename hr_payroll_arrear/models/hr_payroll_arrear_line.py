from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError


class HrMealBillLine(models.Model):
    _name = 'hr.payroll.arrear.line'
    _description = 'HR Employee Arrear line'

    arear_amount = fields.Integer(string="Amount", required=True,readonly=True,states={'draft': [('readonly', False)]})

    """ Relational Fields """
    parent_id = fields.Many2one(comodel_name='hr.payroll.arrear', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade',readonly=True,states={'draft': [('readonly', False)]})

    _sql_constraints = [
        ('unique_employee_id', 'unique(parent_id, employee_id)',
         'warning!!: You can not use the same employee name'),
    ]

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
        ('adjusted', "Adjusted")
    ], default='draft')

    # Show a msg for minus value
    @api.onchange('bill_amount')
    def _onchange_bill(self):
        if self.arear_amount < 0:
            raise UserError(_('Amount never take negative value!'))


