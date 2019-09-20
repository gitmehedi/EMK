from openerp import api, exceptions, fields, models,_
from odoo.exceptions import UserError

class HrExceptionCompensatoryLeaveWizard(models.TransientModel):
    _name='hr.exception.compensatory.leave.wizard'

    employee_ids = fields.Many2many('hr.employee', 'hr_exception_compensatory_leave_employee_rel',
                                    'compensatory_leave_id', 'employee_id', string='Employees',
                                    domain="[('operating_unit_id','=',operating_unit_id),('id','not in',emp_ids)]")

    @api.multi
    def generate_compensatory_record(self):
        pool_exception_emp = self.env['hr.exception.compensatory.leave']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'rel_exception_leave_id': active_id,
            }
            pool_exception_emp += self.env['hr.exception.compensatory.leave'].create(res)
        return {'type': 'ir.actions.act_window_close'}

class HrExceptionOverTimeWizard(models.TransientModel):
    _name='hr.exception.overtime.wizard'

    employee_ids = fields.Many2many('hr.employee', 'hr_exception_overtime_employee_rel',
                                    'exception_overtime_id', 'employee_id', string='Employees',
                                    domain="[('operating_unit_id','=',operating_unit_id),('id','not in',emp_ids)]")

    @api.multi
    def generate_overtime_record(self):
        pool_overtime_emp = self.env['hr.exception.overtime.duty']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'rel_exception_ot_id': active_id,
            }
            pool_overtime_emp += self.env['hr.exception.overtime.duty'].create(res)
        return {'type': 'ir.actions.act_window_close'}