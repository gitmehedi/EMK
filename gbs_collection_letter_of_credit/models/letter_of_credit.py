from odoo import api, fields, models,_


class LetterOfCredit(models.Model):
    _inherit = "letter.credit"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre')

    @api.multi
    def action_confirm_export(self):
        analytic_account_obj = self.env['account.analytic.account']
        if self.pi_ids_temp:
            company_id = self.pi_ids_temp[0].suspend_security().operating_unit_id.company_id.id
            analytic_account = analytic_account_obj.suspend_security().create({'name': self.name, 'type': 'profit', 'company_id':company_id})
        else:
            analytic_account = analytic_account_obj.suspend_security().create({'name': self.name, 'type': 'profit'})
        self.analytic_account_id = analytic_account.id
        return super(LetterOfCredit, self).action_confirm_export()
