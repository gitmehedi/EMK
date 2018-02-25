from odoo import api, fields, models

class HrEmployeeIouLine(models.Model):
    _name='hr.employee.iou.line'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    repay_amount = fields.Float(string="Repay Amount")

    # Relational fields
    iou_id = fields.Many2one('hr.employee.iou', 'id', ondelete='cascade')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('adjusted', "Adjusted")
    ], string='Status', default='draft', )
