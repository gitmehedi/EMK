from openerp import api, fields, models
from datetime import date

class GbsHrManpowerRequisition(models.Model):
    _name='hr.manpower.requisition'
    _rec_name = ''

    date_ = fields.Date(string='Date', required=True)
    issue_date = fields.Datetime(string='Date of Issue', default=date.today(),required=True)
    job_title = fields.Char(string = 'Job Title', required=True)
    section_and_dept = fields.Selection([
        ('full_time', 'Full Time'),
        ('temporary', 'Temporary'),
        ], string = 'Section & Dept.')
    duration = fields.Integer(string='Duration (Months)')
    replaced_person_name = fields.Char(string = 'For replacement Position, Name of replaced person', required=True)
    justify_for_new_position = fields.Text(string = 'For new Position, Justify the necessity', required=True)
    qualification = fields.Text(string = 'Qualification', required=True)
    age = fields.Text(string = 'Age', required=True)
    training_or_practical_skills = fields.Text(string='Training / Practical experience / Skill', required=True)
    principle_duties = fields.Text(string = 'Principle Duties', required=True)
    #@Todo : requisition_raised_by/reviewd_by/forward_by
    comment_by_co_md = fields.Text(string='Approval / Comments by COO / MD', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('head_of_plant', 'Head of Plant'), ## show / hide head of plant based on operating unit condition
        ('hr_manager', 'HR Manager'),
        ('ceo_cxo', 'CEO/CXO'),
        ('cancel', 'Cancelled'),
        ('declined', 'Declined'),
    ], string='Status', default='draft',)

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

