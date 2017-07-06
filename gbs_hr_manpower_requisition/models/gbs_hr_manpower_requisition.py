from openerp import api, fields, models
from datetime import date

class GbsHrManpowerRequisition(models.Model):
    _name='hr.manpower.requisition'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_current_employee, readonly=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id',string='Department', store=True, readonly=True)
    issue_date = fields.Datetime(string='Date of Request', default=date.today(), readonly=True)
    emp_head_count = fields.Integer(string='Head Count', readonly=True) # emp count of the dept of form creating user, write a compute finc
    expected_date = fields.Date(string='Expected Date', required=True)
    replaced_or_new = fields.Selection([('replaced','Replace'), ('new','New')], string='Replace or New') # radio
    replace_of_whom_emp_id = fields.Many2one('hr.employee', string="Replace of Whom") # only current users employee
    replace_of_whom_designation = fields.Many2one('hr.job', string="Designation", related='replace_of_whom_emp_id.job_id', readonly=True)
    no_of_employee = fields.Integer(string = 'No. of Employee', required=True)
    reson_or_justification = fields.Text(string = 'Reason / Justification')
    no_of_joined = fields.Integer(string = 'No. of Joined')

    ###### Below fields are okay
    qualification = fields.Text(string = 'Qualification', required=True)
    age = fields.Text(string = 'Age', required=True)
    training_or_practical_skills = fields.Text(string='Training / Practical experience / Skill', required=True)
    principle_duties = fields.Text(string = 'Principle Duties', required=True)
    comment_by_co_md = fields.Text(string='Comments', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('verify', 'Verify'), ## show / hide head of plant based on operating unit condition
        ('justify', 'Justify'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], string='Status', default='draft',
        help=" Verify is for Head of Plant, Justify is for HR Manager, Approve is for CXO")

    #employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    #department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department')
    #amount = fields.Float(string="Amount", required=True)
    #calculate_amount = fields.Float(string="Amount", default=0)
    #due = fields.Float(string="Due", compute='_compute_amount_value')
    # Relational fields
    #line_ids = fields.One2many('hr.employee.iou.line','repay_id', string="Line Ids")

    # @api.depends('amount')
    # def _compute_amount_value(self):
    #     for record in self:
    #         sum_val = sum([s.repay_amount for s in record.line_ids])
    #         record.due = record.amount - sum_val

    # @api.multi
    # def action_confirm(self):
    #     self.state = 'confirm'
    #
    # @api.multi
    # def action_repay(self):
    #     print 'Hello! Repay'
    #

