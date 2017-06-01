from openerp import api, fields, models, exceptions,_
from openerp.exceptions import UserError, ValidationError


class HrMealBillLine(models.Model):
    _name = 'hr.meal.bill.line'
    _description = 'HR meal bill line'    
    
    bill_amount = fields.Integer(string="Amount", required=True)
    
    """ Relational Fields """
    parent_id = fields.Many2one(comodel_name='hr.meal.bill',ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee",ondelete='cascade')


    _sql_constraints = [
        ('unique_employee_id', 'unique(parent_id, employee_id)',
         'warning!!: You can not use the same employee name'),
    ]

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')

# Show a msg for minus value
    @api.onchange('bill_amount')
    def _onchange_bill(self):
        if self.bill_amount < 0:
            raise UserError(_('Amount naver take negative value!'))


