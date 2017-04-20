from openerp import models, fields
from openerp import api

class HrEmployeeMobileBillLimit(models.Model):
    _name = 'hr.employee.mobile.bill.line'
    _order = "effective_date desc"

    limit = fields.Float(string="Mobile Bill Limit", required=True, default=0)
    effective_date = fields.Date('Effective Date', required=True)
    """ Relational Fields """
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,store=True)
    parent_id = fields.Many2one('hr.mobile.bill.limit')


    """All function which process data and operation"""
    @api.depends('employee_id')
    @api.onchange('employee_id')
    def onchange_employee(self):
        for recode in self:
            if recode.parent_id.effective_bill_date:
                recode.effective_date = recode.parent_id.effective_bill_date




