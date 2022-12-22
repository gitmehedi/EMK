from odoo import fields, models, api


class CommissionConfiguration(models.Model):
    _inherit = ['mail.thread']

    _name = 'commission.configuration'
    _description = 'Commission Configuration'

    name = fields.Char(string="Configuration Name", required=True, track_visibility="onchange")
    customer_type = fields.Many2one('res.customer.type', string='Customer Type', required=True, track_visibility="onchange")
    functional_unit = fields.Many2one('res.branch', string='Functional Unit', required=True, track_visibility="onchange")
    process = fields.Selection([
        ('not_applicable', 'No need commission refund'),
        ('textbox', 'Textbox on Product Commission/Refund Approval'),
        ('checkbox', 'Checkbox on Product Commission/Refund Approval')
    ], string='Process', required=True,
        help='''If textbox selected commission or refund will be calculated based on product commission/refund amount approval.\n If checkbox selected commission or refund will be calculated monthly/yearly based on 
        slab wise configuration.''', track_visibility="onchange")
    show_packing_mode = fields.Boolean(string='Show Packing Mode', default=False,
                                       required=True, track_visibility="onchange", help='Show packing mode in product commission/refund/pricelist approval')
    auto_load_commission_refund_in_so_line = fields.Boolean(string='Auto Load', default=False, track_visibility="onchange", required=True,
                                                            help='''Auto load commission/refund value in sale order line''')
    commission_provision = fields.Selection([
        ('invoice_validation', 'At Invoice Validation'),
        ('customer_collection', 'At Customer Payment Collection')
    ], string='Provision', track_visibility="onchange")

    cpc_type = fields.Selection(
        string='Payment Collection Type',
        selection=[('batch', 'Batch'), ('per_collection', 'Per Collection'), ],
        help="Customer payment collection type",
        required=False, track_visibility="onchange",
    )
    show_discount = fields.Boolean(string='Show Discount', required=False, track_visibility="onchange")
    show_tax = fields.Boolean(string='Show Tax', required=False, track_visibility="onchange")
    so_readonly_field = fields.Boolean(string='Enable Readonly (Unit Price, Commission, Refund, Tax)', required=False, track_visibility="onchange")

    _sql_constraints = [('customer_type_functional_unit_uniq', 'unique(customer_type,functional_unit)', 'A configuration already exist with the given Customer Type and Functional Unit.')]
