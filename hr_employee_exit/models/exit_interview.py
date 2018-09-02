from odoo import fields, models, api, _

class EmployeeEixtInterview(models.Model):
    _name = 'employee.exit.interview'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'Employee Exit Interview'

    employee_code = fields.Char('Employee Code',related='employee_id.code',requiered=True)
    #function = fields.Char('Function',requiered=True)
    location = fields.Char('Location',related='employee_id.work_location', requiered=True)
    joining_date = fields.Date(string='Date of Joining',requiered=True)
    resignation_date = fields.Date(string='Date of Resignation',requiered=True)
    leaving_date = fields.Date(string='Date of Leaving',requiered=True)
    employee_id = fields.Many2one('hr.employee',string = 'Employee Name',requiered=True)
    emp_department = fields.Many2one('hr.department', string='Department Name', related='employee_id.department_id', requiered=True)
    emp_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id', requiered=True)
    supervisor_id = fields.Many2one('hr.employee',string = 'Supervisor',requiered=True)
    supervisor_designation = fields.Many2one('hr.job', string='Supervisor Designation', related='supervisor_id.job_id', requiered=True)
    line_ids = fields.One2many('employee.exit.interview.line','exit_interview_id','rel_exit_interview')
    question_set_ids = fields.One2many('question.set','interview_id','rel_question_set')
    check_box1 = fields.Boolean(string='Most Definitely',default=False)
    # is_active = fields.Boolean(string='Active', default=True)
    check_box2 = fields.Boolean(string='With Reservations',default=False)
    check_box3 = fields.Boolean(string='No',default=False)
    contract_add = fields.Text(string='Contact Address')
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

    @api.one
    def action_submit(self):
        self.state = 'submit'
        self.line_ids.write({'state':'submit'})
        self.question_set_ids.write({'state':'submit'})

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


class EmployeeEixtInterview(models.Model):
    _name = 'employee.exit.interview.line'

    factor= fields.Char('Factor')
    critical_incidents= fields.Char('Critical Incidents')
    point= fields.Float('Points')
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