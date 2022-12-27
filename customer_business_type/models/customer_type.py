from odoo import api, fields, models, _


class ResCustomerType(models.Model):
    _inherit = ['mail.thread']

    _name = 'res.customer.type'
    _description = 'Customer Type'

    name = fields.Char(required=True, track_visibility="onchange")
    customer_type = fields.Selection(
        string='Customer Type',
        selection=[('retail', 'Retal'), ('corporate', 'Corporate'), ], track_visibility="onchange"
    )

    is_retail = fields.Boolean('Is Retail Customer?', track_visibility="onchange")
    is_corporate = fields.Boolean('Is Corporate Customer?', track_visibility="onchange")

    @api.onchange('customer_type')
    def onchange_customer_type(self):
        self.is_retail = self.customer_type == "retail"
        self.is_corporate = self.customer_type == "corporate"
