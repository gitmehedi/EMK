from openerp import api, fields, models

class HrEmployeeIou(models.Model):
    _name='hr.employee.iou'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
    ], string='Status', default='draft',)

    amount = fields.Float(string="Amount", required=True)
    due = fields.Float(string="Due", required=True)

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_repay(self):
        print 'Hello! Repay'


