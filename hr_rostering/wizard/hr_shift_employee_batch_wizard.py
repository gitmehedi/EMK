from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrShiftBatchEmployees(models.TransientModel):
    _name = 'hr.batch.employees'
    _description = 'Create Batch for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_shift_employee_group_rel', 'shift_id', 'employee_id', 'Employees')

    @api.multi
    def generate_record(self):
        pool_shift_emp = self.env['hr.shifting.history']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.shift.employee.batch'].browse(active_id).read(['effective_from', 'effective_end', 'shift_id'])
        effective_from = run_data.get('effective_from')
        effective_end = run_data.get('effective_end')
        shift_id=run_data.get('shift_id')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        print shift_id[0]
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            # history_data = self.env['hr.shifting.history'].onchange_employee_id(shift_id,effective_from, effective_end, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'shift_id': shift_id[0],
                'effective_from': effective_from,
                'effective_end': effective_end,
                'shift_batch_id': active_id,
            }
            pool_shift_emp += self.env['hr.shifting.history'].create(res)
        return {'type': 'ir.actions.act_window_close'}