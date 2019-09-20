from odoo import api, fields, models, exceptions,_
from odoo.exceptions import UserError, ValidationError


class HrEmployeeMobileBillLimit(models.Model):
    _name = 'hr.employee.mobile.bill.line'
    _order = "effective_date desc"

    limit = fields.Integer(string="Mobile Bill Limit", required=True, default=0)
    effective_date = fields.Date('Effective Date', required=True)

    """ Relational Fields """
    parent_id = fields.Many2one(comodel_name='hr.mobile.bill.limit', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade')


    _sql_constraints = [
        ('unique_employee_id', 'unique(parent_id, employee_id)',
         'warning!!: You can not use the same employee name'),
    ]


    """All function which process data and operation"""
    @api.depends('employee_id')
    @api.onchange('employee_id')
    def onchange_employee(self):
        for recode in self:
            if recode.parent_id.effective_bill_date:
                recode.effective_date = recode.parent_id.effective_bill_date


    # Show a msg for minus value
    @api.onchange('limit')
    def _onchange_bill(self):
        if self.limit < 0:
            raise UserError(_('Mobile Bill Limit never take negative value!'))
