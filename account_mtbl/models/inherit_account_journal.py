from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['account.journal','mail.thread']

    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    currency_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    operating_unit_id = fields.Many2one(track_visibility='onchange',string='Branch')
    default_credit_account_id = fields.Many2one(track_visibility='onchange')
    default_debit_account_id = fields.Many2one(track_visibility='onchange')
    refund_sequence = fields.Boolean(track_visibility='onchange')
    update_posted = fields.Boolean(track_visibility='onchange')
    group_invoice_lines = fields.Boolean(track_visibility='onchange')
    show_on_dashboard = fields.Boolean(track_visibility='onchange')