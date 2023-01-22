from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.model
    # def default_payable_acc(self):
    #     return self.env['account.account'].search([
    #         ('internal_type', '=', 'payable'),
    #         ('deprecated', '=', False)],
    #         order='id ASC', limit=1)

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number')
    tin = fields.Char(string='TIN Number')
    # property_account_payable_id = fields.Many2one(default=default_payable_acc,
    #                                               company_dependent=False)
