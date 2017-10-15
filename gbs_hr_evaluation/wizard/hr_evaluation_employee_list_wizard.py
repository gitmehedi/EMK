from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HREvaluationEmployeeListWizard(models.TransientModel):
    _name = 'hr.evaluation.employee.list.wizard'
    _description = 'Genarate Evaluation form for selected employee'

    employee_ids = fields.Many2many('hr.employee', 'hr_evaluation_employee_rel',
                                    'evaluation_id', 'employee_id', string='Employees')

    @api.multi
    def generate_record(self):
        pool_evaluation_emp = self.env['hr.performance.evaluation']
        pool_criteria_emp = self.env['hr.evaluation.criteria.line']
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
            pool_evaluation_emp += self.env['hr.performance.evaluation'].create(res)

        for i in pool_evaluation_emp.search([('rel_plan_id','=',active_id)]):
            for criteria in self.env['hr.evaluation.criteria'].search([('is_active','=',True)]):
                criteria_res = {
                    'seq': criteria.seq,
                    'name': criteria.name,
                    'marks': criteria.marks,
                    'rel_evaluation_id': i.id,
                }
                pool_criteria_emp += self.env['hr.evaluation.criteria.line'].create(criteria_res)

        return {'type': 'ir.actions.act_window_close'}