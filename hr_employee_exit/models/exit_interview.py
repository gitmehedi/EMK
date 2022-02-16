from odoo import fields, models, api, _
from psycopg2 import IntegrityError
from odoo.exceptions import UserError, ValidationError
from odoo.addons.opa_utility.helper.utility import Utility


class EmployeeEixtInterview(models.Model):
    _name = 'employee.exit.interview'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'employee_id'
    _description = 'Employee Exit Interview'

    def _get_employee(self):
        domain = [('id', '=', -1)]
        employee_list = []
        exit_request = self.env['hr.emp.exit.req'].search([('state', '=', 'validate')])
        for each in exit_request:
            employee_list.append(each.employee_id.id)
        if employee_list:
            domain = [('id', 'in', employee_list)]
            return domain
        return domain

    employee_code = fields.Char('Employee Code', related='employee_id.employee_number', readonly=True)
    location = fields.Char('Location', related='employee_id.work_location', readonly=True, track_visibility="onchange")
    joining_date = fields.Date(related='employee_id.initial_employment_date', string='Date Of Join', readonly=True)
    resignation_date = fields.Date(string='Date of Resignation')
    leaving_date = fields.Date(string='Date of Leaving')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, domain=_get_employee,track_visibility="onchange")
    # employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain=_default_employee,
    #                               track_visibility="onchange")
    emp_department = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',
                                     readonly=True, track_visibility="onchange")
    emp_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id', readonly=True,
                                      track_visibility="onchange")
    supervisor_id = fields.Many2one('hr.employee', string='Supervisor', required=True, track_visibility="onchange")
    supervisor_designation = fields.Many2one('hr.job', string='Supervisor Designation', readonly=True,
                                             related='supervisor_id.job_id', track_visibility="onchange")
    line_ids = fields.One2many('employee.exit.interview.line', 'exit_interview_id', 'rel_exit_interview',
                               track_visibility="onchange")
    question_set_ids = fields.One2many('question.set', 'interview_id', 'rel_question_set', track_visibility="onchange")
    recommend = fields.Selection([('one', 'Most Definitely'),
                                  ('two', 'With Reservations'),
                                  ('three', 'No')], 'Syllabus')
    permission = fields.Selection([('yes', 'Yes'),
                                   ('no', 'No')])
    contract_add = fields.Text(string='Contact Address')
    comment_supervisor = fields.Text(string='Comment By Supervisor')
    comment_hr = fields.Text(string='Comment By HR')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('validate', 'Supervisor Approve'),
        ('approved', ' HR Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft', track_visibility='onchange')

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.leaving_date = ''
        self.resignation_date = ''
        emp = self.env['hr.emp.exit.req'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        if emp:
            self.leaving_date = emp.last_date
            self.resignation_date = emp.req_date
        else:
            pass

    @api.multi
    def action_reset(self):
        self.state = 'draft'
        self.line_ids.write({'state': 'draft'})
        self.question_set_ids.write({'state': 'draft'})

    @api.multi
    def action_submit(self):
        self.state = 'submit'
        self.line_ids.write({'state': 'submit'})
        self.question_set_ids.write({'state': 'submit'})
        vals = []
        factor_pool = self.env['factors.set'].search([])
        for fac in factor_pool:
            vals.append((0, 0, {
                'factor': fac.id,
            }))
        self.line_ids = vals

    @api.one
    def action_validate(self):
        self.state = 'validate'
        self.line_ids.write({'state': 'validate'})
        self.question_set_ids.write({'state': 'validate'})

    @api.one
    def action_approved(self):
        self.state = 'approved'
        self.line_ids.write({'state': 'approved'})
        self.question_set_ids.write({'state': 'approved'})

    @api.one
    def action_done(self):
        self.state = 'done'
        self.line_ids.write({'state': 'done'})
        self.question_set_ids.write({'state': 'done'})

    # @api.model
    # def default_create(self):
    #     factor_pool = self.env['factors.set'].search([])
    #     for fac in factor_pool:
    #         self.line_ids.write({
    #             'factor': fac.name,
    #         })


class EmployeeEixtInterviewLine(models.Model):
    _name = 'employee.exit.interview.line'

    factor = fields.Many2one('factors.set', 'Factors')
    critical_incidents = fields.Char('Critical Incidents')
    point = fields.Float('Points')
    exit_interview_id = fields.Many2one('employee.exit.interview')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('validate', 'Supervisor Approve'),
        ('approved', ' HR Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft')


class EmployeeOpinion(models.Model):
    _name = 'question.set'

    question = fields.Char('Questions')
    answer = fields.Text('Answers')
    interview_id = fields.Many2one('employee.exit.interview')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('validate', 'Supervisor Approve'),
        ('approved', ' HR Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft')


class FactorsSet(models.Model):
    _name = 'factors.set'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Factor Set'

    name = fields.Char('Name', track_visibility='onchange', required=True)
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Utility.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Utility.UNLINK_WARNING))
            try:
                return super(FactorsSet, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Utility.UNLINK_INT_WARNING))