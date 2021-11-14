from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    operating_unit_required = fields.Boolean(string='Operating Unit', compute='_compute_required', store=False)
    partner_required = fields.Boolean(string='Partner', compute='_compute_required', store=False)
    analytic_account_required = fields.Boolean(string='Analytic Account', compute='_compute_required', store=False)
    department_required = fields.Boolean(string='Department', compute='_compute_required', store=False)
    cost_center_required = fields.Boolean(string='Cost Center', compute='_compute_required', store=False)

    @api.depends('account_id')
    def _compute_required(self):
        for rec in self:
            rec.operating_unit_required = rec.account_id.user_type_id.operating_unit_required
            rec.partner_required = rec.account_id.user_type_id.partner_required
            rec.analytic_account_required = rec.account_id.user_type_id.analytic_account_required
            rec.department_required = rec.account_id.user_type_id.department_required
            rec.cost_center_required = rec.account_id.user_type_id.cost_center_required

    cost_center_required_on_journal = fields.Boolean(string='Cost Center Is Required On Journal Entry',
                                                     compute='_compute_cost_center_required_on_journal', store=False)

    @api.depends('account_id')
    def _compute_cost_center_required_on_journal(self):
        for rec in self:
            rec.cost_center_required_on_journal = rec.account_id.user_type_id.cost_center_required_on_journal
