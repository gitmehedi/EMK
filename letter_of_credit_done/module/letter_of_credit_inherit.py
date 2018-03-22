from odoo import api, fields, models,_
from odoo.exceptions import UserError,ValidationError



class LetterOfCreditInherit(models.Model):
    _inherit = 'letter.credit'

    gate_in_ids = fields.One2many('lc.evaluation.line', 'rel_job_id', string='')
    comment = fields.Text(string='Comments')

    @api.multi
    def action_lc_eva_in_button(self):
        if self.lc_value > 0.0:
            raise ValidationError(_("Your shipment is not done!"))

        res = self.env.ref('letter_of_credit_done.lc_evaluation_wizard')
        result = {
            'name': _('LC Done'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.evaluation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
        return result

    @api.multi
    def lc_done_action_window1(self):
        domain = [('rel_job_id', '=', self.id)]
        res = self.env.ref('letter_of_credit_done.lc_evaluation_wizard')
        result = {
            'name': _('LC Done'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.evaluation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': domain,
            'context': {'comment': self.comment or False},
            'readonly': True,
        }
        return result

    @api.multi
    def action_confirm(self):
        res = super(LetterOfCreditInherit, self).action_confirm()
        pool_criteria_emp = self.env['lc.evaluation.line']
        for criteria in self.env['hr.employee.criteria'].search(
                [('is_active', '=', True), ('type', '=', 'lc_evaluation')]):
            criteria_res = {
                'name': criteria.name,
                'marks': criteria.marks,
                'rel_job_id': self.id,
            }
            pool_criteria_emp += self.env['lc.evaluation.line'].create(criteria_res)
        return res
