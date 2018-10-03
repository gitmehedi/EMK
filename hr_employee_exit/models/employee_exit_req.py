from odoo import models, fields, api, exceptions,tools,_
import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError



class EmployeeExitReq(models.Model):
    _name = 'hr.emp.exit.req'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _rec_name = 'employee_id'
    _order = 'state asc'

    def last_days(self):
        ldate = datetime.date.today() + relativedelta(months=1)
        return ldate

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    emp_notes = fields.Text(string='Employee Notes')
    reason_for_exit = fields.Text(string='Reason for Leaving',track_visibility='onchange')
    department_notes = fields.Text(string='Department Manager Notes')
    req_date = fields.Date('Request Date', default=fields.Date.today(), track_visibility='onchange',
                           required=True)
    last_date = fields.Date('Last Day of Work', default=last_days,track_visibility='onchange',
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
         ('validate', 'Approved')],
        'Status', readonly=True, copy=False, default='draft',
        help='The status is set to \'To Submit\', when a Exit request is created.\
            \nThe status is \'To Approve\', when exit request is confirmed by user.\
            \nThe status is \'Refused\', when exit request is refused by manager.\
            \nThe status is \'Approved\', when exit request is approved by manager.',track_visibility='onchange')

    employee_id = fields.Many2one('hr.employee', select=True, invisible=False,track_visibility='onchange',default=_current_employee)
    job_id = fields.Many2one('hr.job', string='Job Title', related='employee_id.job_id',track_visibility='onchange')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, copy=False)
    manager_id = fields.Many2one('hr.employee', related='employee_id.parent_id', track_visibility='onchange',
                                 help='This area is automatically filled by the user who validate the exit process')
    department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange',
                                    related='employee_id.department_id')
    parent_id = fields.Many2one('hr.emp.exit.req', string='Parent')
    confirm_by = fields.Many2one('res.users', string='Confirmed By', readonly=True,
                                   default=lambda self: self.env.user)
    approver1_by = fields.Many2one('res.users', string="Approved By Department Manager",
                                   readonly=True)
    approver2_by = fields.Many2one('res.users', string="Approved By HR Manager", readonly=True)
    checklists_ids = fields.One2many('hr.exit.checklists.line','checklist_id',ondelete="cascade")
    pen_checklists_ids = fields.One2many('pendding.checklists.line','pen_checklist_id',ondelete="cascade")

    # compute current_user_is_approver
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



    # Button actions
    @api.multi
    def exit_reset(self):
        self.write({'state': 'draft'})
        self.checklists_ids = 0
        return True

    #exit request confirm
    @api.multi
    def exit_confirm(self):
        self.checklists_ids = []
        vals = []
        confg_checklist_pool = self.env['hr.exit.configure.checklists'].search([('is_active', '=', True)])
        for record in confg_checklist_pool:
            if record.applicable_empname_id or record.applicable_department_id or record.applicable_jobtitle_id:
                if self.job_id or self.employee_id or self.department_id:
                    if record.applicable_empname_id == self.employee_id or record.applicable_department_id == self.department_id or record.applicable_jobtitle_id == self.job_id:
                        for config in record.checklists_ids:
                            vals.append((0, 0, {
                                'checklist_item_id': config.checklist_item_id,
                                'responsible_department': config.responsible_department,
                                'responsible_emp': config.responsible_emp,
                                'state': 'not_received'
                            }))
        self.checklists_ids = vals
        self.confirm_by = self.env.user
        #self.send_mail_exit_request_confirm()
        return self.write({'state': 'confirm','confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def send_mail_exit_request_confirm(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        model_data_pool = self.env['ir.model.data'].search([('name', '=', 'group_hr_manager')], limit=1)
        record_id = model_data_pool.res_id
        manager = self.env['res.groups'].search([('id', '=', record_id)]).users
        emailto = []
        for eml in manager:
            login = eml.login
            emailto.append(login)
        emailto.append(self.employee_id.parent_id.user_id.login)
        for email in emailto:
            template = self.env.ref('hr_employee_exit.example_exit_req_email_template')
            template.write({
                'subject': "Exit Request",
                'email_from': email_server_obj,
                'email_to': email})
            self.env['mail.template'].browse(template.id).send_mail(self.id)

    # exit request approved
    @api.multi
    def exit_validate(self):
        self.approver1_by = self.env.user
        #self.send_mail_template()
        return self.write({'state': 'validate1', 'approved1_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def send_mail_template(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        model_data_pool = self.env['ir.model.data'].search([('name', '=', 'group_hr_manager')], limit=1)
        record_id = model_data_pool.res_id
        manager = self.env['res.groups'].search([('id', '=', record_id)]).users
        emailto = []
        for eml in manager:
            login = eml.login
            emailto.append(login)
        emailto.append(self.employee_id.user_id.login)
        for email in emailto:
            template = self.env.ref('hr_employee_exit.email_template_exit_req_approved')
            template.write({
                'subject': "Exit Request has been approved",
                'email_from': email_server_obj,
                'email_to': email})
            self.env['mail.template'].browse(template.id).send_mail(self.id)


    #exit request done(final approval)
    @api.multi
    def exit_done(self):
        self.pen_checklists_ids = []
        self.employee_id.stages_history = []
        vals = []
        emp_status = []
        line_obj = self.env['hr.exit.checklists.line'].search(
            [('checklist_id', '=', self.id)])
        for record in line_obj:
                vals.append((0, 0, {
                    'checklist_item_id': record.checklist_item_id,
                    'responsible_department': record.responsible_department,
                    'responsible_emp': record.responsible_emp,
                    'employee_id': record.employee_id,
                    'state': 'not_received'
                }))
        self.pen_checklists_ids = vals
        self.approver2_by = self.env.user
        emp_status.append((0, 0, {
            'start_date': datetime.date.today(),
            'end_date': self.last_date,
            'duration':0,
            'state': 'relieved'
        }))
        self.employee_id.stages_history = emp_status
        self.employee_id.write({'state': 'relieved'})
        return self.write({'state': 'validate','approved2_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    # Exit request cancel
    @api.multi
    def exit_refuse(self):
        for emp_exit in self:
            if emp_exit.state == 'validate1':
                self.write({'state': 'refuse'})
            else:
                self.write({'state': 'refuse'})
        #self.send_mail_exit_request_cancel()
        return True

    @api.multi
    def send_mail_exit_request_cancel(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        template = self.env.ref('hr_employee_exit.send_mail_exit_request_cancel')
        template.write({
            'subject': "Exit request has been cancelled",
            'email_from': email_server_obj,
            'email_to': self.employee_id.user_id.login})
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.constrains('req_date', 'last_date')
    def _check_last_date(self):
        if self.req_date > self.last_date :
            raise Warning('Last Date must be grater than request date.')



class EmpReqChecklistsLine(models.Model):
    _name = "hr.exit.checklists.line"
    _rec_name = 'checklist_item_id'
    _inherit = ['mail.thread','ir.needaction_mixin']

    employee_id = fields.Many2one('hr.employee',related='checklist_id.employee_id',track_visibility='onchange')
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', string='Checklist Item',required=True)
    remarks = fields.Text(string='Remarks',track_visibility='onchange')
    state = fields.Selection([
        ('received', "Received"),
        ('not_received', "Not Received")
    ],'Status',default='not_received')

    # Relational fields
    checklist_id = fields.Many2one('hr.emp.exit.req',ondelete="cascade")
    responsible_department = fields.Many2one('hr.department', ondelete='set null', string='Responsible Department')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User')

class PendingChecklistsLine(models.Model):
    _name = "pendding.checklists.line"
    _rec_name = 'checklist_item_id'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    employee_id = fields.Many2one('hr.employee', related='pen_checklist_id.employee_id', track_visibility='onchange')
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', string='Checklist Item', required=True)
    remarks = fields.Text(string='Remarks', track_visibility='onchange')
    state = fields.Selection([
        ('received', "Received"),
        ('not_received', "Not Received")
    ], 'Status', default='not_received')

    # Relational fields
    #checklist_id = fields.Many2one('hr.emp.exit.req', ondelete="cascade")
    pen_checklist_id = fields.Many2one('hr.emp.exit.req', ondelete="cascade")
    responsible_department = fields.Many2one('hr.department', ondelete='set null', string='Responsible Department')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User')

    status = fields.Selection([('draft', 'Draft'), ('verify', 'Verified')],
                              readonly=True, copy=False,
                              default='draft', track_visibility='onchange')
    @api.multi
    def check_list_verify(self):
        exit_req_obj = self.env['hr.exit.checklists.line'].search(
            [('checklist_id','=',self.pen_checklist_id.id)])
        for exit_line in exit_req_obj:
            if exit_line.responsible_department:
                if exit_line.checklist_item_id == self.checklist_item_id and exit_line.responsible_department == self.responsible_department:
                    exit_line.remarks = self.remarks
                    exit_line.write({'state': 'received'})
            elif exit_line.responsible_emp:
                if exit_line.checklist_item_id == self.checklist_item_id and exit_line.responsible_emp == self.responsible_emp:
                    exit_line.remarks = self.remarks
                    exit_line.write({'state': 'received'})
            else:
                pass
        #self.send_mail_received_item()
        return self.write({'status': 'verify', 'state': 'received'})

    @api.multi
    def send_mail_received_item(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        model_data_pool = self.env['ir.model.data'].search([('name', '=', 'group_hr_manager')], limit=1)
        record_id = model_data_pool.res_id
        manager = self.env['res.groups'].search([('id', '=', record_id)]).users
        emailto = []
        for eml in manager:
            login = eml.login
            emailto.append(login)
        emailto.append(self.employee_id.parent_id.user_id.login)
        emailto.append(self.employee_id.user_id.login)
        for email in emailto:
            template = self.env.ref('hr_employee_exit.email_template_received_item')
            template.write({
                'subject': "Items has been received",
                'email_from': email_server_obj,
                'email_to': email})
            self.env['mail.template'].browse(template.id).send_mail(self.id)