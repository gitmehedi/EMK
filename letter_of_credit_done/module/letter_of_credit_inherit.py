from odoo import api, fields, models,_


class LetterOfCreditInherit(models.Model):
    _inherit = 'letter.credit'

    gate_in_ids = fields.One2many('lc.confirmation.line', 'rel_job_id', string='')

    @api.multi
    def action_lc_eva_in_button(self):
        res = self.env.ref('letter_of_credit_done.lc_confirmation_wizard')
        result = {
            'name': _('LC Confirmation'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.confirmation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
        return result

    @api.multi
    def action_confirm(self):
        res = super(LetterOfCreditInherit, self).action_confirm()
        pool_criteria_emp = self.env['lc.confirmation.line']
        for criteria in self.env['hr.employee.criteria'].search(
                [('is_active', '=', True), ('type', '=', 'lc_evaluation')]):
            criteria_res = {
                'name': criteria.name,
                'marks': criteria.marks,
                'rel_job_id': self.id,
            }
            pool_criteria_emp += self.env['lc.confirmation.line'].create(criteria_res)
        return res
