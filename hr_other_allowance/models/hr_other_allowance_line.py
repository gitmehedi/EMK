from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError


class HrOtherAllowanceLine(models.Model):
    _name = 'hr.other.allowance.line'
    _description = 'HR Employee Other Allowance line'

    other_allowance_amount = fields.Integer(string="Amount", required=True,readonly=True,states={'draft': [('readonly', False)]})

    """ Relational Fields """
    parent_id = fields.Many2one(comodel_name='hr.other.allowance', ondelete='cascade')
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
    @api.onchange('other_allowance_amount')
    def _onchange_bill(self):
        if self.other_allowance_amount < 0:
            raise UserError(_('Amount never take negative value!'))


