from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ConfirmationJudgement(models.TransientModel):
    _name = 'lc.confirmation.wizard'


    comment = fields.Text(string='Comments')
    @api.model
    def _load_judgement(self):
        form_id = self.env.context.get('active_id')
        #evalution = self.env['hr.job.confirmation'].search([('id', '=', form_id)])
        evalution = self.env['letter.credit'].search([('id', '=', form_id)])
        evalution_ids = self.criteria_line_ids
        for record in evalution.gate_in_ids:
            evalution_ids += evalution_ids.new({
                'parent_id': record.id,
                'name': record.name,
                'marks': record.marks,
                'obtain_marks': record.obtain_marks,
                'comment' : record.comment,
            })
        return evalution_ids

    criteria_line_ids = fields.One2many('lc.confirmation.wizard.line', 'rel_lc_id',default=_load_judgement)

    @api.multi
    def save_evaluating(self):
        # form_id = self.env.context.get('active_id')
        # evaluation_form_pool = self.env['letter.credit'].search([('id', '=', form_id)])
        # evaluation_form_pool.write(
        #     {'comment': self.comment})
        for wizard_line in self.criteria_line_ids:
            evaluating_line_form_pool = self.env['lc.confirmation.line'].search(
                [('id', '=', wizard_line.parent_id)])
            evaluating_line_form_pool.write({
                'obtain_marks': wizard_line.obtain_marks,
                'comment' : wizard_line.comment,
            })


class ConfirmationJudgementLine(models.TransientModel):
    _name = 'lc.confirmation.wizard.line'

    rel_lc_id = fields.Many2one('lc.confirmation.wizard')
    name = fields.Char(string='Criteria Name')
    marks = fields.Float(string='Total Marks')
    obtain_marks = fields.Float(string='Obtain Marks')
    parent_id = fields.Integer(string='Parent Id')
    comment = fields.Text(string='Comments')


    @api.constrains('obtain_marks')
    def _check_obtain_marks(self):
        for x in self:
            if x.obtain_marks > x.marks:
                raise ValidationError(_("Obtain marks can not be greater then total marks"))
