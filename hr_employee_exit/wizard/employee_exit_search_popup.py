from openerp import models, fields, api, exceptions

class EmployeeExitSearch(models.TransientModel):
    _name = 'hr.exit.employee.exit.search.popup'
    
    employee_id = fields.Many2one('hr.employee', string='Name of Employee', required=True,
                           help='Please select employee name.')
    
    @api.multi
    def action_search_employee_exit(self):
        return True
