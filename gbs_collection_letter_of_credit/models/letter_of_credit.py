from odoo import api, fields, models, _


class LetterOfCredit(models.Model):
    _inherit = "letter.credit"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre')

    @api.multi
    def action_confirm_export(self):
        analytic_account_obj = self.env['account.analytic.account']
        if self.pi_ids_temp:
            company_id = self.pi_ids_temp[0].suspend_security().operating_unit_id.company_id.id
            analytic_account = analytic_account_obj.suspend_security().create(
                {'name': self.name, 'type': 'profit', 'company_id': company_id})
        else:
            analytic_account = analytic_account_obj.suspend_security().create({'name': self.name, 'type': 'profit'})
        self.analytic_account_id = analytic_account.id
        return super(LetterOfCredit, self).action_confirm_export()

    @api.multi
    def action_update_lc_number(self):
        vals = {
            'lc_id': self.id,
        }
        message_id = self.env['update.lc.number.confirmation'].create({
            'current_lc_number': self.name
        })
        return {
            'name': _('Confirmation : Are you sure to update this LC Number?'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'update.lc.number.confirmation',
            'context': vals,
            'res_id': message_id.id,
            'target': 'new'
        }
