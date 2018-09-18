from odoo import fields, models, api,_
from odoo.exceptions import Warning as UserError


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
        return {'domain': {'public_holidays_line': [('public_type_id', '=', self.public_holidays_title.id)]}}


    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    @api.one
    @api.constrains('public_holidays_line', 'operating_unit_id')
    def _check_public_holidays_line(self):
        domain = [('public_holidays_line', '=', self.public_holidays_line.id),
                  ('operating_unit_id', '=', self.operating_unit_id.id),
                 ('id', '!=', self.id)]
        if self.search_count(domain):
            raise UserError('You can\'t create duplicate exceptions holiday for same operating unit')

        return True

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        com_pool = self.env['hr.exception.compensatory.leave'].search([('rel_exception_leave_id', '=', self.id)])
        holiday_status_pool=self.env['hr.holidays.status'].search([('name', '=', 'Comp. Leave')])
        if com_pool:
            for i in com_pool:
                holidays_create_pool= self.env['hr.holidays'].create({
                    'name':("%s's %s on %s [%s]") % (i.employee_id.name,holiday_status_pool.name,self.public_holidays_line.name ,self.public_holidays_line.date ),
                    'type': 'add',
                    'number_of_days_temp':1,
                    'holiday_type': 'employee',
                    'holiday_status_id': holiday_status_pool.id,
                    'employee_id': i.employee_id.id,
                    'department_id':i.employee_id.department_id.id,
                    'leave_year_id':self.public_holidays_title.year_id.id,
                    'notes':("Getting 1 day(s) Compensatory Leave instead of %s [%s]") % (self.public_holidays_line.name , self.public_holidays_line.date),
                    'state':'validate',
                })
        self.write({'state': 'approved'})


    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_assign_compensatory(self):
        ot_pool = self.env['hr.exception.overtime.duty'].search([('rel_exception_ot_id', '=', self.id)])
        com_pool = self.env['hr.exception.compensatory.leave'].search([('rel_exception_leave_id', '=', self.id)])
        emp_ids = []
        if com_pool and ot_pool:
            for com_obj in com_pool:
                emp_ids.append(com_obj.employee_id.id)
            for ot_obj in ot_pool:
                emp_ids.append(ot_obj.employee_id.id)
        elif com_pool:
            for com_obj in com_pool:
                emp_ids.append(com_obj.employee_id.id)
        elif ot_pool:
            for ot_obj in ot_pool:
                emp_ids.append(ot_obj.employee_id.id)


        res = self.env.ref('hr_holiday_exception.view_hr_compensatory_leave_wizard_form')
        result = {
            'name': _('Exception Compensatory Leave'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'hr.exception.compensatory.leave.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            # 'domain': [('employee_ids.operating_unit_id', '=', self.operating_unit_id.id)],
            'context': {'create': False, 'emp_ids': emp_ids, 'operating_unit_id': self.operating_unit_id.id},
        }
        return result

    @api.multi
    def action_assign_overtime(self):
        ot_pool = self.env['hr.exception.overtime.duty'].search([('rel_exception_ot_id', '=', self.id)])
        com_pool=self.env['hr.exception.compensatory.leave'].search([('rel_exception_leave_id','=',self.id)])
        emp_ids=[]
        if com_pool and ot_pool:
            for com_obj in com_pool:
                emp_ids.append(com_obj.employee_id.id)
            for ot_obj in ot_pool:
                emp_ids.append(ot_obj.employee_id.id)
        elif com_pool:
            for com_obj in com_pool:
                emp_ids.append(com_obj.employee_id.id)
        elif ot_pool:
            for ot_obj in ot_pool:
                emp_ids.append(ot_obj.employee_id.id)

        res = self.env.ref('hr_holiday_exception.view_hr_exception_overtime_wizard_form')
        result = {
            'name': _('Exception Overtime'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'hr.exception.overtime.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            # 'domain': [('employee_ids.operating_unit_id', '=', self.operating_unit_id.id)],
            'context': {'create': False,'emp_ids':emp_ids,'operating_unit_id':self.operating_unit_id.id},
        }
        return result

    @api.multi
    def unlink(self):
        for excep in self:
            if excep.state!='draft':
                raise UserError(_('You can not delete in this state!!'))
            else:
                return super(HrEmployeeExceptionHolidaysBatch, self).unlink()


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