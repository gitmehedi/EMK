from odoo import models, fields, api, _


class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    operating_unit_required = fields.Boolean(string='Operating Unit')
    partner_required = fields.Boolean(string='Partner')
    analytic_account_required = fields.Boolean(string='Analytic Account')
    department_required = fields.Boolean(string='Department')
    cost_center_required = fields.Boolean(string='Cost Center')
    is_bank_type = fields.Boolean(string='Is Bank Type?')