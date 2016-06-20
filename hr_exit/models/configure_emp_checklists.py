from openerp import models, fields, api, exceptions

class ConfigureEmpChecklist(models.Model):
    _name = "hr.exit.configure.emp.checklists"


    _rec_name = 'employee_id'
    employee_id = fields.Many2one('hr.employee', select=True, invisible=False,
                                  default=lambda self: self._employee_gets())
    check_list_type_id = fields.Many2one('hr.exit.checklist.type', string="Checklist Types")
    check_list_item = fields.Many2one('hr.exit.checklist.item', string="Checklist Types")
    
    # Relational fields
    checklist_name = fields.Char(string='Name', size=100)
    checklists_id = fields.Many2one('hr.exit.configure.checklists', string="Checklist")
    status = fields.Boolean(string='Status', default= False)
    state = fields.Selection([('draft', 'To Submit'),('validate', 'Approved')])
    emp_name=fields.Many2one('hr.employee',string='Employee Name', help='Please enter responsible user name.')

    department=fields.Many2one('hr.department', ondelete='set null', string='Department', help='Please enter responsible department name.')

    #emp_checklist_ids = fields.One2many('hr.exit.configure.checklists.line','check_list_emp_id')
    check_list_line_ids = fields.One2many('hr.exit.configure.checklists.line','check_list_line_id')


    @api.multi
    def exit_submit(self):
        return 1


    @api.multi
    def _employee_gets(self):
        # emp_id = context.get('default_employee_id', False)
        # if emp_id:
        #     return emp_id
        ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if ids:
            return ids[0]
        return False
    
