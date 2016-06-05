from openerp import models, fields, api, exceptions


class EmployeeExitReq(models.Model):
    _name = 'employee.exit.req'

    descriptions = fields.Text(string='Descriptions')
    note = fields.Char(size=200, string='Note',readonly=True)
    req_date = fields.Date(string='Request Date')
    last_date = fields.Date(string='Last Day of Work')
    state = fields.Selection(
        [('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
         ('validate1', 'Second Approval'), ('validate2', 'Third Approval'), ('validate', 'Approved')],
        'Status', readonly=True, copy=False, default='draft',
        help='The status is set to \'To Submit\', when a Exit request is created.\
            \nThe status is \'To Approve\', when exit request is confirmed by user.\
            \nThe status is \'Refused\', when exit request is refused by manager.\
            \nThe status is \'Approved\', when exit request is approved by manager.')

    employee_id = fields.Many2one('hr.employee',select=True, invisible=False)
    user_id = fields.Float(compute='_compute_user_id')
    manager_id = fields.Many2one('hr.employee', invisible=False, readonly=True, copy=False,
                                      help='This area is automatically filled by the user who validate the exit process')
    #parent_id = fields.Many2one('employee.exit.req', string='Parent')
    department_id = fields.Float(string='Department', compute='_compute_department_id')
    category_id = fields.Many2one('hr.employee.category', string = 'Category', help='Category of Employee')
    manager_id2 = fields.Many2one('hr.employee', string= 'Second Approval', readonly=True, copy=False,
                                       help='This area is automaticly filled by the user who validate the exit with second level (If exit type need second validation)')
    manager_id3 = fields.Many2one('hr.employee', string= 'Third Approval', readonly=True, copy=False,
                                       help='This area is automaticly filled by the user who validate the exit with third level (If exit type need third validation)')
    # can_reset = fields.function(
    #         _get_can_reset,
    #         type='boolean')



    def _get_can_reset(self):

        #user can edit the exit request if it is draft/to approve stage
        result = False

        return result


    @api.multi
    @api.depends('employee_id')
    def _compute_user_id(self):
        return 1

    @api.multi
    @api.depends('employee_id')
    def _compute_department_id(self):
        return 1



# class Inherit_hr_employee(models.Model):
#     _inherit = "hr.employee"

