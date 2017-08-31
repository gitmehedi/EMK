from datetime import date
from openerp import fields, models, api,_
from openerp.exceptions import Warning as UserError


class HrEmployeeHolidaysBatch(models.Model):
    _name = 'hr.holidays.exception.employee.batch'
    _description = 'Employee Holidays Exception'
    _rec_name = 'name'
    _order = "id"

    name=fields.Char(string='Name',required=True)
    operating_unit_id=fields.Many2one('operating.unit',string='Operating Unit',required=True)
    public_holidays_title=fields.Many2one('hr.holidays.public',string='Public Holidays Title',required=True)

    compensatory_leave_ids=fields.One2many('hr.exception.compensatory.leave','rel_exception_leave_id',string='Compensatory Leave')
    overtime_duty_ids=fields.One2many('hr.exception.overtime.duty','rel_exception_ot_id',string='Overtime Duty')
    public_holidays_ids = fields.One2many('hr.exception.public.holidays.line', 'rel_exception_id', string="Public Holidays Details")

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        self.public_holidays_title=[]
        self.public_holidays_ids=[]
        return {'domain': {'public_holidays_title': [('operating_unit_ids', '=', self.operating_unit_id.id)]}}

    @api.onchange('public_holidays_title')
    def onchange_public_holidays_title(self):
        if self.public_holidays_title:
            if self.operating_unit_id:
                val=[]
                query="""select public_holiday_id from public_holiday_operating_unit_rel where operating_unit_id=%s and public_holiday_id=%s"""
                self._cr.execute(query, tuple([self.operating_unit_id.id, self.public_holidays_title.id]))
                qry_public_holiday_id = self._cr.fetchone()
                public_holiday_id= qry_public_holiday_id[0]
                if public_holiday_id:
                    holidays_line_pool=self.env['hr.holidays.public.line'].search([('public_type_id','=',public_holiday_id)])
                    for i in holidays_line_pool:
                        val.append((0, 0, {'name': i.name,
                                           'holiday_date': i.date,
                                           }))

                        self.public_holidays_ids = val
            else:
                raise UserError(_('Select Operating Unit!!'))

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

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

class HrOverTimeAlterDuty(models.Model):
    _name = 'hr.exception.public.holidays.line'
    _description = 'Exception Public Holidays'

    """Relational Fields"""
    rel_exception_id=fields.Many2one('hr.holidays.exception.employee.batch', string='Overtime Duty')
    name = fields.Char('Name')
    holiday_date = fields.Date('Date')

