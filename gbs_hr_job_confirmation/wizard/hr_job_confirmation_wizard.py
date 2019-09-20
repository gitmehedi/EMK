from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ConfirmationEmpComments(models.TransientModel):
    _name = 'job.confirmation.employee.comment.wizard'

    emp_comment = fields.Text(string='Comment', default=lambda self: self.env.context.get('emp_comment'))

    @api.multi
    def save_record(self):
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write(
            {'emp_comment': self.emp_comment})
        return {'type': 'ir.actions.act_window_close'}



class ConfirmingPersonsComments(models.TransientModel):
    _name = 'job.confirmation.persons.comment.wizard'

    supervisor_comment = fields.Text(string='Supervisor Comments',
                                     default=lambda self: self.env.context.get('supervisor_comment'))
    hod_comment = fields.Text(string='Head of Department Comments',
                              default=lambda self: self.env.context.get('hod_comment'))
    plant_incharge_comment = fields.Text(string='Plant In-Charge Comments',
                                         default=lambda self: self.env.context.get('plant_incharge_comment'))
    hr_manager_comment = fields.Text(string='HR Manager Comments',
                                     default=lambda self: self.env.context.get('hr_manager_comment'))
    cxo_comment = fields.Text(string='Chief Officer Comments',
                              default=lambda self: self.env.context.get('cxo_comment'))

    @api.multi
    def save_hr_manager_comment(self):
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write(
            {'hr_manager_comment': self.hr_manager_comment})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def save_cxo_comment(self):
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write(
            {'cxo_comment': self.cxo_comment})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def save_supervisor_comment(self):
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write(
            {'supervisor_comment': self.supervisor_comment})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def save_hod_comment(self):
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write(
            {'hod_comment': self.hod_comment})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def save_plant_incharge_comment(self):
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write(
            {'plant_incharge_comment': self.plant_incharge_comment})
        return {'type': 'ir.actions.act_window_close'}


class ConfirmationJudgement(models.TransientModel):
    _name = 'job.confirmation.judgement.wizard'

    @api.model
    def _load_judgement(self):
        form_id = self.env.context.get('active_id')
        evalution = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evalution_ids = self.criteria_line_ids
        for record in evalution.criteria_line_ids:
            evalution_ids += evalution_ids.new({
                'parent_id':record.id,
                'seq': record.seq,
                'name': record.name,
                'marks': record.marks,
                'obtain_marks': record.obtain_marks,
            })
        return evalution_ids

    judgment_promotion = fields.Boolean(string='Promotion',default=lambda self: self.env.context.get('judgment_promotion'))
    judgment_observation = fields.Boolean(string='Place Under Observation',default=lambda self: self.env.context.get('judgment_observation'))
    judgment_increment = fields.Boolean(string='Increment',default=lambda self: self.env.context.get('judgment_increment'))
    judgment_training_requirement = fields.Boolean(string='Training Requirement',default=lambda self: self.env.context.get('judgment_training_requirement'))

    criteria_line_ids = fields.One2many('job.confirmation.judgement.wizard.line', 'rel_judgement_wizard_id',
                                        default=_load_judgement)

    @api.multi
    def save_evaluating_judgement(self):
        for wizard_line in self.criteria_line_ids:
            evaluating_line_form_pool = self.env['hr.job.confirmation.criteria.line'].search(
                [('id', '=', wizard_line.parent_id)])
            evaluating_line_form_pool.write({
                'obtain_marks': wizard_line.obtain_marks,
            })
        form_id = self.env.context.get('active_id')
        evaluation_form_pool = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evaluation_form_pool.write({
            'judgment_promotion': self.judgment_promotion,
            'judgment_observation': self.judgment_observation,
            'judgment_increment': self.judgment_increment,
            'judgment_training_requirement': self.judgment_training_requirement,})

        return {'type': 'ir.actions.act_window_close'}



class HRConfirmationCriteriaLine(models.TransientModel):
    _name = 'job.confirmation.judgement.wizard.line'
    _order = "seq asc"

    rel_judgement_wizard_id = fields.Many2one('job.confirmation.judgement.wizard')
    parent_id = fields.Integer(string='Parent Id')
    seq = fields.Integer(string='Sequence')
    name = fields.Char(string='Criteria Name')
    marks = fields.Float(string='Total Marks')
    obtain_marks = fields.Float(string='Obtain Marks')

    @api.constrains('obtain_marks')
    def _check_obtain_marks(self):
        for x in self:
            if x.obtain_marks > x.marks:
                raise ValidationError(_("Obtain marks can not be greater then total marks"))
