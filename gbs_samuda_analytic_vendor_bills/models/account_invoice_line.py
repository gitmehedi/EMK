from odoo import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    analytic_account_required = fields.Boolean(string='Analytic Account', compute='_compute_required', store=False)

    @api.depends('account_id')
    def _compute_required(self):
        for rec in self:
            rec.analytic_account_required = rec.account_id.analytic_account_required

