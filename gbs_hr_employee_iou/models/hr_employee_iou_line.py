from openerp import api, fields, models

class HrEmployeeIouLine(models.Model):
    _name='hr.employee.iou.line'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    repay_amount = fields.Float(string="Repay Amount")

    # Relational fields
    repay_id = fields.Many2one('hr.employee.iou', 'id', ondelete='cascade')
