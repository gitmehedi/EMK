from odoo import models, fields, api, _


class AccountAccountType(models.Model):
    _name = 'account.account.type'
    _inherit = ['account.account.type', 'mail.thread']

    operating_unit_required = fields.Boolean(string='Operating Unit', track_visibility='onchange')
    partner_required = fields.Boolean(string='Partner', track_visibility='onchange')
    analytic_account_required = fields.Boolean(string='Analytic Account', track_visibility='onchange')
    department_required = fields.Boolean(string='Department', track_visibility='onchange')
    cost_center_required = fields.Boolean(string='Cost Center', track_visibility='onchange')
    is_bank_type = fields.Boolean(string='Is Bank Type?', track_visibility='onchange')

    name = fields.Char(string='Account Type', required=True, translate=True, track_visibility='onchange')
    type = fields.Selection([
        ('other', 'Regular'),
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('liquidity', 'Liquidity'),
        ('liquidity', 'Liquidity'),
        ('view', 'View')
    ], required=True, default='other',
        help="The 'Internal Type' is used for features available on " \
             "different types of accounts: liquidity type is for cash or bank accounts" \
             ", payable/receivable is for vendor/customer accounts.", track_visibility='onchange')