from odoo import api, fields, models, _
from lxml import etree

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

    customer = fields.Boolean(string='Is a Customer', default=False, track_visibility='onchange',
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

    # custmer type will be used to calculate commission and refund
    customer_type = fields.Selection(string='Customer Type', selection=[('coorporate', 'Coorporate'), ('dealer', 'Dealer')], default="coorporate")


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                   toolbar=toolbar,
                                                                   submenu=submenu)

        doc = etree.XML(res['arch'])
        no_create_edit_button = self.env.context.get('no_create_edit_button')

        if not self.env.user.has_group('gbs_application_group.group_sales_vendor_manager'):
            if no_create_edit_button:
                if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                    for node_form in doc.xpath("//kanban"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
                    for node_form in doc.xpath("//tree"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
                    for node_form in doc.xpath("//form"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')

        no_create_edit_button_customer = self.env.context.get('no_create_edit_button_customer')
        if not self.env.user.has_group('gbs_application_group.group_sales_customer_manager'):
            if no_create_edit_button_customer:
                if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                    for node_form in doc.xpath("//kanban"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
                    for node_form in doc.xpath("//tree"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
                    for node_form in doc.xpath("//form"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')

        res['arch'] = etree.tostring(doc)
        return res





