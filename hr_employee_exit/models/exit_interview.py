from odoo import fields, models, api, _

class EmployeeEixtInterview(models.Model):
    _name = 'employee.exit.interview'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'Employee Exit Interview'


    employee_code = fields.Char('Employee Code',related='employee_id.code',required=True,readonly=True)
    location = fields.Char('Location',related='employee_id.work_location', required=True,readonly=True)
    joining_date = fields.Date(string='Date of Joining',required=True)
    resignation_date = fields.Date(string='Date of Resignation',required=True)
    leaving_date = fields.Date(string='Date of Leaving',required=True)
    employee_id = fields.Many2one('hr.employee',string = 'Employee',required=True)
    emp_department = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',readonly=True, required=True)
    emp_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id',readonly=True, required=True)
    supervisor_id = fields.Many2one('hr.employee',string = 'Supervisor',required=True)
    supervisor_designation = fields.Many2one('hr.job', string='Supervisor Designation',readonly=True, related='supervisor_id.job_id', required=True)
    line_ids = fields.One2many('employee.exit.interview.line','exit_interview_id','rel_exit_interview')
    question_set_ids = fields.One2many('question.set','interview_id','rel_question_set')
    recommend = fields.Selection([('one', 'Most Definitely'),
                                   ('two', 'With Reservations'),
                                   ('three', 'No')], 'Syllabus')
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

    @api.multi
    def action_reset(self):
        self.state = 'draft'
        self.line_ids.write({'state': 'draft'})
        self.question_set_ids.write({'state': 'draft'})

    @api.multi
    def action_submit(self):
        self.state = 'submit'
        self.line_ids.write({'state':'submit'})
        self.question_set_ids.write({'state':'submit'})
        factor_pool = self.env['factors.set'].search([])
        # for fac in factor_pool:
        #     self.line_ids.create({
        #         'factor': fac.id,
        #     })
        # return

    @api.one
    def action_validate(self):
        self.state = 'validate'
        self.line_ids.write({'state':'validate'})
        self.question_set_ids.write({'state':'validate'})

    @api.one
    def action_approved(self):
        self.state = 'approved'
        self.line_ids.write({'state':'approved'})
        self.question_set_ids.write({'state':'approved'})

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


class EmployeeEixtInterview(models.Model):
    _name = 'employee.exit.interview.line'


    factor = fields.Many2one('factors.set','Factors')
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

    name = fields.Char('Name')