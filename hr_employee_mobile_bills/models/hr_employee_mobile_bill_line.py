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
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    company_id = fields.Many2one('res.company', string='Company')

    device_employee_acc = fields.Char(string="AC No", store=False, readonly=True,
                                      compute='_compute_device_employee_acc')

    @api.depends('employee_id')
    def _compute_device_employee_acc(self):
        for rec in self:
            rec.device_employee_acc = rec.employee_id.device_employee_acc

    _sql_constraints = [
        ('unique_employee_id', 'unique(parent_id, employee_id)',
         'warning!!: You can not use the same employee name'),
    ]

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def onchange_employee(self):
        """All function which process data and operation"""
        for recode in self:
            if recode.parent_id.effective_bill_date:
                recode.effective_date = recode.parent_id.effective_bill_date

    @api.constrains('limit')
    def _check_bill_amount(self):
        # Show a msg for minus value
        if self.limit < 0:
            raise ValidationError(_('Mobile Bill Limit never take negative value!'))
