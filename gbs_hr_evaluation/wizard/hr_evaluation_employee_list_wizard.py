from odoo import api, fields, models, _

class HREvaluationEmployeeListWizard(models.TransientModel):
    _name = 'hr.evaluation.employee.list.wizard'
    _description = 'Genarate Evaluation form for selected employee'

    employee_ids = fields.Many2many('hr.employee', 'hr_evaluation_employee_rel',
                                    'evaluation_id', 'employee_id', string='Employees')
