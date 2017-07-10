from openerp import api, fields, models
from datetime import date

class HREmployeeRequisition(models.Model):
    _name='hr.employee.requisition'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Requisition By", default=_current_employee, readonly=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id',string='Department', store=True, readonly=True)
    issue_date = fields.Datetime(string='Date of Request', default=date.today(), readonly=True)
    emp_head_count = fields.Integer(string='Current Emp(s)', readonly=True)
    expected_date = fields.Date(string='Expected Date', required=True)
    replaced_or_new = fields.Selection([('replaced','Replace'), ('new','New')], string='Replace or New')
    replace_of_whom_emp_id = fields.Many2one('hr.employee', string="Replace of Whom") # only current users employee
    replace_of_whom_designation = fields.Many2one('hr.job', string="Designation", related='replace_of_whom_emp_id.job_id', readonly=True)
    no_of_employee = fields.Integer(string = 'No. of Req. Emp(s)', required=True)
    reson_or_justification = fields.Text(string = 'Reason / Justification')
    no_of_joined = fields.Integer(string = 'No. of Joined') # Will be used later
    qualification = fields.Text(string = 'Qualification', required=True)
    age = fields.Text(string = 'Age', required=True)
    training_or_practical_skills = fields.Text(string='Training / Practical experience / Skill', required=True)
    principle_duties = fields.Text(string = 'Principle Duties', required=True)
    comment_by_co_md = fields.Text(string='Comments', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('verify', 'Verify'), ## @Todo show / hide head of plant based on operating unit condition
        ('justify', 'Justify'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], string='Status', default='draft',
        help=" Verify is for Head of Plant, Justify is for HR Manager, Approve is for CXO")

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_approve(self):
        self.state = 'approved'

    @api.multi
    def action_decline(self):
        self.state = 'declined'

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_justify(self):
        self.state = 'justify'

