from openerp import models, fields, _

class HrEmployeeMobileBillLimit(models.Model):
    _name = 'hr.employee.mobile.bill.line'
    _order = "effective_date desc"

    limit = fields.Float(string="Mobile Bill Limit", required=True, default=0)
    effective_date = fields.Date('Effective Date', required=True)
    """ Relational Fields """
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    parent_id = fields.Many2one('hr.mobile.bill.limit')



