from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_receivable_id = fields.Many2one(required=False)
    property_account_payable_id = fields.Many2one(required=False)

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number')
    tin = fields.Char(string='TIN Number')

    ############ for log in customer,supplier,vendor,cnf ###############


    name = fields.Char(index=True, track_visibility='onchange')

    customer = fields.Boolean(string='Is a Customer', default=True, track_visibility='onchange',
                               help="Check this box if this contact is a customer.")
    supplier = fields.Boolean(string='Is a Vendor',track_visibility='onchange',
                               help="Check this box if this contact is a vendor. "
                               "If it's not checked, purchase people will not see it when encoding a purchase order.")
    is_cnf = fields.Boolean(string='Is a C&F Agent', track_visibility='onchange')

    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency", company_dependent=True,track_visibility='onchange',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",track_visibility='onchange',
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]", track_visibility='onchange',
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    active = fields.Boolean(default=True, track_visibility='onchange')










