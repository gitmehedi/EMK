from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cost_center_required_on_journal = fields.Boolean(string='Cost Center Is Required On Journal Entry',
                                                     compute='_compute_cost_center_required_on_journal', store=False)

    @api.depends('account_id')
    def _compute_cost_center_required_on_journal(self):
        for rec in self:
            rec.cost_center_required_on_journal = rec.account_id.user_type_id.cost_center_required_on_journal
