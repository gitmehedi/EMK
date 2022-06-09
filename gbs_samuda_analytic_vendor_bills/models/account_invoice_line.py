from odoo import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    analytic_account_required = fields.Boolean(string='Analytic Account', compute='_compute_required', store=False)

    @api.depends('account_id','invoice_id')
    def _compute_required(self):
        for rec in self:
            if rec.invoice_id and rec.account_id:
                if rec.invoice_id.type=='in_invoice':
                    rec.analytic_account_required = rec.account_id.analytic_account_required

    cost_center_required = fields.Boolean(string='Cost Center', compute='_compute_cost_center_required', store=False)

    @api.depends('account_id','invoice_id')
    def _compute_cost_center_required(self):
        for rec in self:
            if rec.invoice_id and rec.account_id:
                if rec.invoice_id.type=='in_invoice':
                    rec.cost_center_required = rec.account_id.cost_center_required