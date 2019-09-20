from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HRJobConfirmationEmployeeListWizard(models.TransientModel):
    _name = 'hr.job.confirmation.employee.list.wizard'
    _description = 'Genarate Job Confirmation form for selected employee'

    employee_ids = fields.Many2many('hr.employee', 'hr_job_employee_rel',
                                    'job_confirmation_id', 'employee_id', string='Employees',
                                    domain = "[('operating_unit_id', '=',operating_unit_id )]")

    @api.multi
    def generate_record(self):
        pool_evaluation_emp = self.env['hr.job.confirmation']
        [data] = self.read()
        active_id = self.env.context.get('active_id')

        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'emp_department': employee.department_id.id,
                'emp_designation': employee.job_id.id,
                'joining_date': employee.initial_employment_date,
                'manager_id': employee.parent_id.id,
                'rel_plan_id': active_id,
                # 'state':'supervisor',
            }
            pool_evaluation_emp += self.env['hr.job.confirmation'].create(res)

        return {'type': 'ir.actions.act_window_close'}

