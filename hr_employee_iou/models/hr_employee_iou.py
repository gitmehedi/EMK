from odoo import api, fields, models

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
    calculate_amount = fields.Float(string="Amount", default=0)
    due = fields.Float(string="Due", compute='_compute_amount_value')

    # Relational fields
    line_ids = fields.One2many('hr.employee.iou.line','iou_id', string="Line Ids")

    @api.depends('amount')
    def _compute_amount_value(self):
        for record in self:
            sum_val = sum([s.repay_amount for s in record.line_ids])
            record.due = record.amount - sum_val


    @api.multi
    def action_confirm(self):
        self.state = 'confirm'
        self.line_ids.write({'state':'confirm'})
    @api.multi
    def action_repay(self):
        print 'Hello! Repay'


