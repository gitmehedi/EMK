from odoo import models, fields, api, exceptions,_
import datetime
import time


class EmployeeExitReq(models.Model):
    _name = 'hr.emp.exit.req'

    _rec_name = 'employee_id'
    emp_notes = fields.Text(string='Employee Notes')
    reason_for_exit = fields.Text(string='Reason for Leaving')
    department_notes = fields.Text(string='Department Manager Notes')
    req_date = fields.Date('Request Date', default=fields.Date.today(),
                           required=True)
    last_date = fields.Date('Last Day of Work', default=fields.Date.today(),
                            required=True)
    confirm_date = fields.Date(string="Confirm Date", default=datetime.date.today(),
                               readonly=True)
    approved1_date = fields.Date(string='Approval Date(Department Manager',
                                 readonly=True)
    approved2_date = fields.Date(string="Approval Date(HR Manager)",
                                 _defaults=lambda *a: time.strftime('%Y-%m-%d'),
                                 readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    state = fields.Selection(
        [('draft', 'To Submit'),
         ('cancel', 'Cancelled'),
         ('confirm', 'To Approve'),
         ('refuse', 'Refused'),
         ('validate1', 'Second Approval'),
         ('validate2', 'Third Approval'),
         ('validate', 'Approved')],
        'Status', readonly=True, copy=False, default='draft',
        help='The status is set to \'To Submit\', when a Exit request is created.\
            \nThe status is \'To Approve\', when exit request is confirmed by user.\
            \nThe status is \'Refused\', when exit request is refused by manager.\
            \nThe status is \'Approved\', when exit request is approved by manager.')

    employee_id = fields.Many2one('hr.employee', select=True, invisible=False)
    job_id = fields.Many2one('hr.job', string='Job Title', related='employee_id.job_id')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, copy=False)
    manager_id = fields.Many2one('hr.employee', related='employee_id.parent_id',
                                 help='This area is automatically filled by the user who validate the exit process')
    department_id = fields.Many2one('hr.department', string='Department',
                                    related='employee_id.department_id')
    category_id = fields.Many2one('hr.employee.category', string='Category',
                                  help='Category of Employee')
    parent_id = fields.Many2one('hr.emp.exit.req', string='Parent')
    confirm_by = fields.Many2one('res.users', string='Confirmed By', readonly=True,
                                   default=lambda self: self.env.user)
    approver1_by = fields.Many2one('res.users', string="Approved By Department Manager",
                                   readonly=True)
    approver2_by = fields.Many2one('res.users', string="Approved By HR Manager", readonly=True)
    checklists_ids = fields.One2many('hr.exit.configure.checklists.line', 'checklists_id')

    @api.one
    def _compute_current_user_is_approver(self):
        user = self.env.user.browse(self.env.uid)
        if self.manager_id:
            if self.manager_id.user_id.id == self.env.user.id:
                self.current_user_is_approver = True
            else:
                self.current_user_is_approver = False
        elif user.has_group('hr.group_hr_manager'):
            self.current_user_is_approver = True
        else:
            pass

    @api.multi
    def exit_reset(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def exit_confirm(self):
        self.confirm_by = self.env.user
        return self.write({'state': 'confirm','confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def exit_validate(self):
        self.approver1_by = self.env.user
        return self.write({'state': 'validate1', 'approved1_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def exit_first_validate(self):
        self.approver2_by = self.env.user
        return self.write({'state': 'validate','approved2_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def exit_refuse(self):
        for emp_exit in self:
            if emp_exit.state == 'validate1':
                self.write({'state': 'refuse'})
            else:
                self.write({'state': 'refuse'})
        return True

    @api.multi
    @api.onchange('employee_id')
    def on_change_employee(self):
        self.checklists_ids = []
        vals = []
        confg_checklist_pool = self.env['hr.exit.configure.checklists'].search([('is_active','=',True)])
        for record in confg_checklist_pool:
            if record.applicable_empname_id:
                if record.applicable_empname_id == self.employee_id:
                    for config in record.checklist_item_ids:
                        vals.append((0, 0, {
                                            'name': config.name,
                                            #'employee': config.applicable_empname_id,
                                            }))
        self.checklists_ids = vals