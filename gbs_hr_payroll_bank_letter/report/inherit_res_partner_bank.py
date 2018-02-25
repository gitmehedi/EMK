from odoo import api, fields, models

class InheritResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    is_payroll_account = fields.Boolean(String='Is Payroll A/C', hint='aaaaa', default=False)
