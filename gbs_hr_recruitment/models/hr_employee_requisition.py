from odoo import _,api, fields, models
from datetime import datetime
from openerp.exceptions import Warning as UserError

class HREmployeeRequisition(models.Model):
    _name = 'hr.employee.requisition'
    _inherit = ['mail.thread']

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def get_domain_id(self):
        user = self.env.user.browse(self.env.uid)
        if user.has_group('hr_recruitment.group_hr_recruitment_user') or user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            query = """SELECT  distinct(department_id) FROM hr_employee WHERE operating_unit_id in %s """
            self._cr.execute(query, [tuple(user.operating_unit_ids.ids)])
            res = []
            for data in self._cr.fetchall():
                if data[0] != res:
                    res.append(data[0])
            return [('id', 'in', res)]
        elif user.has_group('gbs_application_group.group_dept_manager'):
            return [('manager_id', '=', user.employee_ids.id)]


    name=fields.Char(string="Manpower Requisition Ref", store=True,default = lambda self: _('New'),required = True)
    employee_id = fields.Many2one('hr.employee', string="Requisition By", default=_current_employee, readonly=True)
    department_id = fields.Many2one('hr.department', string='Department',required = True,domain=get_domain_id)
    job_id = fields.Many2one('hr.job', string='Job Title',required='True')
    issue_date = fields.Datetime(string='Date of Request', default = datetime.now(), readonly=True)
    current_no_of_emp = fields.Integer(string='Current Emp(s)', readonly=True,compute='_compute_no_of_employee',store=True)
    expected_date = fields.Date(string='Expected Date', required=True)
    replaced_or_new = fields.Selection([('replaced','Replace'), ('new','New')], string='Replace or New')
    replace_of_whom_emp_id = fields.Many2one('hr.employee', string="Replace of Whom") # only current users employee
    replace_of_whom_designation = fields.Many2one('hr.job', string="Designation", related='replace_of_whom_emp_id.job_id', readonly=True)
    req_no_of_employee = fields.Integer(string = 'No. of Req. Emp(s)', required=True)
    reson_or_justification = fields.Text(string = 'Reason / Justification')
    approved_no_of_emp = fields.Integer(string = 'No. of Approved' ,related='department_id.approved_no_of_emp',readonly=True)
    qualification = fields.Text(string = 'Qualification', required=True)
    age = fields.Integer(string = 'Age', required=True)
    training_or_practical_skills = fields.Text(string='Training / Practical experience / Skill', required=True)
    principle_duties = fields.Text(string = 'Principle Duties', required=True)
    comment_by_co_md = fields.Text(string='Description', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('hr_approve', 'HR Approval'),
        ('cxo_approve', 'Second Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status',track_visibility='onchange', default='draft',
        help=" Verify is for Head of Plant, Justify is for HR Manager, Approve is for CXO")

    factory_or_head_office = fields.Boolean(string='Is Head Office?')

    check_edit_access = fields.Boolean(string='Check', compute='_compute_check_user')

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    def _compute_check_user(self):
        user = self.env.user.browse(self.env.uid)
        for i in self:
            if user.has_group('hr_recruitment.group_hr_recruitment_manager') and i.state == 'hr_approve':
                i.check_edit_access = True
            elif user.has_group('gbs_application_group.group_head_of_plant') and i.state == 'confirmed':
                i.check_edit_access = True
            elif user.has_group('gbs_application_group.group_cxo') and i.state == 'cxo_approve':
                i.check_edit_access = True
            else:
                i.check_edit_access = False

    @api.one
    @api.depends('department_id')
    def _compute_no_of_employee(self):
        if self.department_id:
            pool_emp=self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
            self.current_no_of_emp=len(pool_emp.ids)

    @api.multi
    def action_confirm(self):
        if self.factory_or_head_office:
            self.state='hr_approve'
        else:
            self.state = 'confirmed'

    @api.multi
    def action_hop_approve(self):
        self.state = 'hr_approve'

    @api.multi
    def action_hr_approve(self):
        self.state = 'cxo_approve'

    @api.multi
    def action_cxo_approve(self):
        if self.replaced_or_new=="new":
            dept_pool = self.env['hr.department'].search([('id','=',self.department_id.id)])
            no_of_approval_emp=dept_pool.approved_no_of_emp
            res_num=no_of_approval_emp+self.req_no_of_employee
            dept_pool.write({'approved_no_of_emp': res_num})
        self.state = 'approved'


    @api.multi
    def action_decline(self):
        self.state = 'declined'

    @api.multi
    def action_reset(self):
        self.state = 'draft'

        ####################################################
        # ORM Overrides methods
        ####################################################

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id', False)
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.requisition') or _('New')
        requisition = super(HREmployeeRequisition, self).create(vals)
        requisition.add_follower(employee_id)
        return requisition
        # return super(HREmployeeRequisition, self).create(vals)

    @api.multi
    def write(self, vals):
        employee_id = vals.get('employee_id', False)
        result = super(HREmployeeRequisition, self).write(vals)
        self.add_follower(employee_id)
        return result

    @api.multi
    def unlink(self):
        for excep in self:
            if excep.state != 'draft':
                raise UserError(_('You can not delete in this state!!'))
            else:
                return super(HREmployeeRequisition, self).unlink()