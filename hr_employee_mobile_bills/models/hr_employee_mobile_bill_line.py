from openerp import models, fields, _

class HrEmployeeMobileBillLine(models.Model):
    _name = 'hr.employee.mobile.bill.line'

    limit = fields.Float(string="Mobile Bill Limit", required=True, default=0)
    effective_date = fields.Date('Effective Date', required=True)
    """ Relational Fields """
    employee_id = fields.Many2one('hr.employee', string="Employee")

    _order = "effective_date desc"

