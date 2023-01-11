from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CommissionConfiguration(models.Model):
    _inherit = ['mail.thread']

    _name = 'commission.configuration'
    _description = 'Commission Configuration'

    name = fields.Char(
        string="Configuration Name",
        track_visibility="onchange"
    )
    customer_type = fields.Many2one(
        'res.customer.type',
        string='Customer Type',
        track_visibility="onchange"
    )
    functional_unit = fields.Many2one(
        'res.branch',
        string='Functional Unit',
        track_visibility="onchange"
    )
    process = fields.Selection(
        [
            ('not_applicable', 'No need commission refund'),
            ('textbox', 'Textbox on Product Commission/Refund Approval'),
            ('checkbox', 'Checkbox on Product Commission/Refund Approval')
        ],
        string='Process',
        store=True,
        help='''If textbox selected commission or refund will be calculated based on product commission/refund amount approval.\n If checkbox selected commission or refund will be calculated monthly/yearly based on 
        slab wise configuration.''',
        track_visibility="onchange"
    )
    show_packing_mode = fields.Boolean(
        string='Show Packing Mode',
        default=False,
        track_visibility="onchange",
        help='Show packing mode in product commission/refund/pricelist approval'
    )
    auto_load_commission_refund_in_so_line = fields.Boolean(
        string='Auto Load',
        default=False,
        track_visibility="onchange",
        force_save=True,
        help='''Auto load commission/refund value in sale order line'''
    )
    auto_load_copy = fields.Boolean(string='Auto Load Copy')
    commission_provision = fields.Selection(
        [
            ('invoice_validation', 'At Invoice Validation'),
            ('customer_collection', 'At Customer Payment Collection')
        ],
        string='Customer Provision',
        store=True,
        track_visibility="onchange"
    )
    show_discount = fields.Boolean(
        string='Show Discount',
        track_visibility="onchange"
    )
    show_tax = fields.Boolean(
        string='Show Tax',
        track_visibility="onchange"
    )
    so_readonly_field = fields.Boolean(
        string='Enable Readonly (Unit Price, Commission, Refund, Tax)',
        track_visibility="onchange"
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company'
    )

    _sql_constraints = [
        ('customer_type_functional_unit_uniq',
         'unique(customer_type,functional_unit)',
         'A configuration already exist with the given Customer Type and Functional Unit.'
         )
    ]

    @api.constrains('process', 'commission_provision')
    def _process_commission_provision_constrains(self):
        if self.process == 'checkbox' and self.commission_provision == 'invoice_validation':
            raise ValidationError(_("Process & Provision combination is not developed yet. Please choose other combination."))

    @api.onchange('so_readonly_field')
    def _onchange_so_readonly_field(self):
        if self.so_readonly_field:
            self.auto_load_commission_refund_in_so_line = True
            self.auto_load_copy = True

    @api.onchange('customer_type')
    def onchange_customer_type(self):
        if self.customer_type:
            if self.customer_type.is_retail:
                self.process = 'checkbox'
                self.commission_provision = 'customer_collection'
            elif self.customer_type.is_corporate:
                self.process = 'textbox'
                self.commission_provision = 'invoice_validation'

    @api.model
    def create(self, values):
        res = super(CommissionConfiguration, self).create(values)
        if 'auto_load_copy' in values:
            res.auto_load_commission_refund_in_so_line = res.auto_load_copy

        if res.customer_type:
            if res.customer_type.is_retail:
                res.process = 'checkbox'
                res.commission_provision = 'customer_collection'
            elif res.customer_type.is_corporate:
                res.process = 'textbox'
                res.commission_provision = 'invoice_validation'

        return res

    @api.multi
    def write(self, values):
        if 'auto_load_copy' in values:
            values['auto_load_commission_refund_in_so_line'] = values['auto_load_copy']

        if 'customer_type' in values:
            customer_type = self.env['res.customer.type'].browse(values['customer_type'])
            if customer_type:
                if customer_type.is_retail:
                    values.update({
                        'process': 'checkbox',
                        'commission_provision': 'customer_collection',
                    })
                elif customer_type.is_corporate:
                    values.update({
                        'process': 'textbox',
                        'commission_provision': 'invoice_validation',
                    })

        res = super(CommissionConfiguration, self).write(values)
        return res
