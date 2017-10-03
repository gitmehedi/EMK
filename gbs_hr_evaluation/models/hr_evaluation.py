from odoo import fields, models, api,_
from odoo.exceptions import UserError

class HRPerformanceEvaluation(models.Model):
    _name='hr.performance.evaluation'
    _inherit = ['mail.thread']
    _description = 'Employee Evaluation'
    _order = "id desc"

    employee_id = fields.Many2one('hr.employee',string = 'Name',requiered=True)
    emp_department = fields.Many2one('hr.department',string = 'Department Name',requiered=True)
    emp_designation = fields.Many2one('hr.job',string = 'Designation',requiered=True)
    joining_date = fields.Date(string = 'Joining Date')

    given_reward = fields.Text(string = 'Reward Given')
    disciplinary_action = fields.Text(string = 'Disciplinary Action')

    total_available_days = fields.Integer(string = 'Total Available Days')
    on_time_attended_days = fields.Integer(string='On Time Attended Days')
    late_attended_days = fields.Integer(string = 'Late Attended Days')
    absent_days = fields.Integer(string = 'Absent')
    casual_leave_days = fields.Integer(string = 'Casual Leave')
    earned_leave_days = fields.Integer(string = 'Earned Leave')
    sick_leave_days = fields.Integer(string = 'Sick Leave')
    extra_purpose_leave_days = fields.Integer(string = 'Extra Purpose Leave')

    emp_comment = fields.Text(string = 'Comment')

    judgment_promotion = fields.Boolean(string = 'Promotion')
    judgment_observation = fields.Boolean(string = 'Place Under Observation')
    judgment_increment = fields.Boolean(string = 'Increment')
    judgment_training_requirement = fields.Boolean(string = 'Training Requirement')

    evaluating_persons_comment = fields.Text(string='Comment',track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('supervisor', 'Confirmed'),
        ('hod_approve', 'HOD Approve'),
        ('gm_approve', 'GM Approve'),
        ('hr_approve', 'HR Approve'),
        ('cxo_approve', 'CXO Approve'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], string='Status', default='draft', track_visibility='onchange')

    ### Relational Fields ###
    rel_plan_id = fields.Many2one('hr.evaluation.plan')
    criteria_line_ids = fields.One2many('hr.evaluation.criteria.line','rel_evaluation_id')

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    def action_confirm(self):
        self.state = 'supervisor'

    @api.multi
    def action_supervisor_approve(self):
        self.state = 'hod_approve'

    @api.multi
    def action_hod_approve(self):
        self.state = 'gm_approve'

    @api.multi
    def action_gm_approve(self):
        self.state = 'hr_approve'

    @api.multi
    def action_hr_approve(self):
        self.state = 'cxo_approve'

    @api.multi
    def action_cxo_approve(self):
        self.state = 'approved'

    @api.multi
    def action_decline(self):
        self.state = 'declined'

    @api.multi
    def action_reset(self):
        self.state = 'draft'

    ####################################################
    # Override methods
    ####################################################

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete in this state.'))
        return super(HRPerformanceEvaluation, self).unlink()


class HREvaluationCriteriaLine(models.Model):
    _name='hr.evaluation.criteria.line'
    _description = 'Evaluation Criteria lines'
    _order = "seq asc"

    rel_evaluation_id = fields.Many2one('hr.performance.evaluation')
    seq = fields.Integer(string = 'Sequence')
    name = fields.Char(string = 'Criteria Name')
    marks = fields.Float(string = 'Total Marks')
    obtain_marks = fields.Float(string = 'Obtain Marks')
