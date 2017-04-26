from openerp import api, fields, models, exceptions
from openerp.exceptions import UserError, ValidationError


class HrLeaveEncashmentLine(models.Model):    
    _name = 'hr.meal.bill.line'
    _description = 'HR meal bill line'    
    
    bill_amount = fields.Char(string="Amount", required=True)
    
    """ Relational Fields """

    
    parent_id = fields.Many2one(comodel_name='hr.meal.bill',ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee",ondelete='cascade')
    #employee_id = fields.Many2one( "hr.meal.bill","employee",required=True)

    _sql_constraints = [
        ('unique_employee_id', 'unique(employee_id)', 'warning!!: You can not use the same employee name'),
    ]

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')
    
    @api.multi
    def unlink(self):
        for line in self:
            if line.state != 'draft':
                raise UserError(_('You can not delete this.'))
        return super(HrLeaveEncashmentLine, self).unlink()