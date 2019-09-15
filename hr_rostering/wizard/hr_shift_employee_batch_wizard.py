from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date

class HrShiftBatchEmployees(models.TransientModel):
    _name = 'hr.batch.employees'
    _description = 'Create Batch for all selected employees'

    effective_from = fields.Date(string='Effective Start Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_shift_employee_group_rel',
                                    'shift_id', 'employee_id', string='Employees')
    shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True,
                               domain="[('state', '=','approved' )]")
    @api.multi
    def generate_record(self):
        pool_shift_emp = self.env['hr.shifting.history']
        [data] = self.read()
        active_id = self.env.context.get('active_id')

        effective_from = self.effective_from
        effective_end = self.effective_end
        shift_id=self.shift_id
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'shift_id': shift_id.id,
                'effective_from': effective_from,
                'effective_end': effective_end,
                'rel_exception_leave_id': active_id,
                'shift_batch_id': active_id,
            }
            pool_shift_emp += self.env['hr.shifting.history'].create(res)
        query = """ UPDATE hr_shift_employee_batch SET effective_from = %s,effective_end=%s,shift_id=%s WHERE id = %s"""
        self._cr.execute(query, tuple([self.effective_from,self.effective_end,self.shift_id.id ,active_id]))
        return {'type': 'ir.actions.act_window_close'}