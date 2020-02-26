from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class HolidayAllowanceWizard(models.TransientModel):
    _name = 'hr.holiday.allowance.wizard'
    __description = 'Create Batch for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_holiday_allowance_group_rel',
                                    'holiday_allowance_id', 'employee_id', string='Employees')

    allowance_date = fields.Date('Allowance Date')

    @api.multi
    def generate_record(self):
        pool_allowance_emp = self.env['hr.holiday.allowance.line']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'emp_allowance_date': self.allowance_date,
                'holiday_allowance_id': active_id,
                'state': 'draft'
            }
            pool_allowance_emp.create(res)
        return {'type': 'ir.actions.act_window_close'}
