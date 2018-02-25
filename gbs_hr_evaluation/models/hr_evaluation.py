from odoo import fields, models, api,_
from odoo.exceptions import UserError,ValidationError

class HRPerformanceEvaluation(models.Model):
    _name='hr.performance.evaluation'
    _inherit = ['mail.thread']
    _description = 'Employee Evaluation'
    _rec_name = 'employee_id'
    _order = "id desc"

    employee_id = fields.Many2one('hr.employee',string = 'Name',requiered=True)
    emp_department = fields.Many2one('hr.department',string = 'Department Name',requiered=True)
    emp_designation = fields.Many2one('hr.job',string = 'Designation',requiered=True)
    joining_date = fields.Date(string = 'Joining Date')
    academic_qualification = fields.Date(string = 'Academic Qualification')
    joining_designation = fields.Date(string = 'Designation On Joining')

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

    supervisor_comment = fields.Text(string='Supervisor Comments',track_visibility='onchange')
    hod_comment = fields.Text(string='Head of Department Comments',track_visibility='onchange')
    plant_incharge_comment = fields.Text(string='Plant In-Charge Comments',track_visibility='onchange')
    hr_manager_comment = fields.Text(string='HR Manager Comments',track_visibility='onchange')
    cxo_comment = fields.Text(string='Chief Officer Comments',track_visibility='onchange')

    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True, copy=False)

    check_access = fields.Boolean(string = 'Check', compute = 'compute_access')

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
    def compute_access(self):
        for h in self:
            if h.employee_id.user_id.id == self.env.user.id:
                h.check_access = False
            else:
                res = h.employee_id.check_1st_level_approval()
                h.check_access = res

    @api.multi
    def action_confirm(self):
        user_manager = self.env['res.users'].search([('id','=',self.manager_id.sudo().user_id.id)])
        if user_manager.has_group('gbs_application_group.group_dept_manager'):
            self.state = 'hod_approve'
        else:
            self.state = 'supervisor'


    @api.multi
    def action_supervisor_approve(self):
        current_user_emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        user_manager = self.env['res.users'].search([('id', '=', current_user_emp_id.parent_id.sudo().user_id.id)])
        if user_manager.has_group('gbs_application_group.group_dept_manager'):
            self.state = 'hod_approve'
        else:
            self.state = 'hr_approve'


    @api.multi
    def action_hod_approve(self):
        current_user_emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        user_manager = self.env['res.users'].search([('id', '=', current_user_emp_id.parent_id.sudo().user_id.id)])
        if user_manager.has_group('gbs_application_group.group_general_manager') or user_manager.has_group('gbs_application_group.group_head_of_plant'):
            self.state = 'gm_approve'
        else:
            self.state = 'hr_approve'


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

    @api.multi
    def action_hr_comment_wizard(self):
        res = self.env.ref('gbs_hr_evaluation.evaluation_hr_comment_wizard')
        result = {
            'name': _('HR Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluation.hr.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'given_reward': self.given_reward or False, 'disciplinary_action': self.disciplinary_action or False},

        }
        return result

    @api.multi
    def action_employee_comment_wizard(self):
        res = self.env.ref('gbs_hr_evaluation.evaluation_employee_comment_wizard')
        result = {
            'name': _('Employee Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluation.employee.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'emp_comment': self.emp_comment or False},
        }
        return result

    @api.multi
    def action_hr_manager_comment(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_hr_manager_comment_wizard')
        result = {
            'name': _('HR Manager Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.persons.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'hr_manager_comment': self.hr_manager_comment or False},
        }
        return result

    @api.multi
    def action_cxo_comment(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_cxo_comment_wizard')
        result = {
            'name': _('Chief Officer Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.persons.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'cxo_comment': self.cxo_comment or False},
        }
        return result

    @api.multi
    def action_supervisor_comment(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_supervisor_comment_wizard')
        result = {
            'name': _('Supervisor Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.persons.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'supervisor_comment': self.supervisor_comment or False},
        }
        return result

    @api.multi
    def action_supervisor_comment(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_supervisor_comment_wizard')
        result = {
            'name': _('Supervisor Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.persons.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'supervisor_comment': self.supervisor_comment or False},
        }
        return result

    @api.multi
    def action_hod_comment(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_hod_comment_wizard')
        result = {
            'name': _('Head of department Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.persons.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'hod_comment': self.hod_comment or False},
        }
        return result

    @api.multi
    def action_plant_incharge_comment(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_plant_incharge_comment_wizard')
        result = {
            'name': _('Plant Incharge Comments'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.persons.comment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'plant_incharge_comment': self.plant_incharge_comment or False},
        }
        return result

    @api.multi
    def action_judge_incharge(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_judgement_wizard')
        result = {
            'name': _('Performance Evaluation'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.judgement.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'judgment_promotion': self.judgment_promotion or False,
                        'judgment_observation': self.judgment_observation or False,
                        'judgment_increment': self.judgment_increment or False,
                        'judgment_training_requirement': self.judgment_training_requirement or False,
                        },
        }
        return result

    @api.multi
    def action_judge_hod(self):
        res = self.env.ref('gbs_hr_evaluation.evaluating_judgement_wizard')
        result = {
            'name': _('Performance Evaluation'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'evaluating.judgement.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'judgment_promotion': self.judgment_promotion or False,
                        'judgment_observation': self.judgment_observation or False,
                        'judgment_increment': self.judgment_increment or False,
                        'judgment_training_requirement': self.judgment_training_requirement or False,
                        },
        }
        return result

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

    @api.constrains('obtain_marks')
    def _check_obtain_marks(self):
        for criteria_line in self:
            if criteria_line.obtain_marks>criteria_line.marks:
                raise ValidationError(_("Obtain marks can not be greater then total marks"))