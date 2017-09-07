from datetime import date
from openerp import fields, models, api,_
from openerp.exceptions import Warning as UserError


class HrEmployeeExceptionHolidaysBatch(models.Model):
    _name = 'hr.holidays.exception.employee.batch'
    _description = 'Employee Holidays Exception'
    _rec_name = 'name'
    _order = "id"

    name=fields.Char(string='Name',required=True)
    operating_unit_id=fields.Many2one('operating.unit',string='Operating Unit',required=True)
    public_holidays_title=fields.Many2one('hr.holidays.public',string='Public Holidays Title',required=True)
    public_holidays_line=fields.Many2one('hr.holidays.public.line',string='Public Holidays',required=True)

    compensatory_leave_ids=fields.One2many('hr.exception.compensatory.leave','rel_exception_leave_id',string='Compensatory Leave')
    overtime_duty_ids=fields.One2many('hr.exception.overtime.duty','rel_exception_ot_id',string='Overtime Duty')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default='draft')

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        self.public_holidays_title=[]
        self.public_holidays_line=[]
        return {'domain': {'public_holidays_title': [('operating_unit_ids', '=', self.operating_unit_id.id)]}}

    @api.onchange('public_holidays_title')
    def onchange_public_holidays_title(self):
        self.public_holidays_line=[]
        if self.public_holidays_title:
            return {'domain': {'public_holidays_line': [('public_type_id', '=', self.public_holidays_title.id)]}}
            # if self.operating_unit_id:
            #
            # else:
            #     raise UserError(_('Select Operating Unit!!'))

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})


class HrCompensatoryLeave(models.Model):
    _name = 'hr.exception.compensatory.leave'
    _description = 'Exception Compensatory Leave'

    """Relational Fields"""
    rel_exception_leave_id=fields.Many2one('hr.holidays.exception.employee.batch', string='Compensatory Leave')
    employee_id = fields.Many2one("hr.employee",string='Employee Name')


class HrOverTimeAlterDuty(models.Model):
    _name = 'hr.exception.overtime.duty'
    _description = 'Exception Overtime Duty'

    """Relational Fields"""
    rel_exception_ot_id=fields.Many2one('hr.holidays.exception.employee.batch', string='Overtime Duty')
    employee_id = fields.Many2one("hr.employee", string='Employee Name')