from odoo import api, fields, models, _


class VendorSecurityDeposit(models.Model):
    _name = 'vendor.security.deposit'
    _description = 'Vendor Security Deposit'

    name = fields.Char(required=False, track_visibility='onchange', string='Deposit Name')
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 track_visibility='onchange',
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    account_id = fields.Many2one('account.account', string='Account', required=True, track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange', states={'draft': [('readonly', False)]},
                          help="amount to be deposited to vendor for security deposit purpose")
    adjusted_amount = fields.Float(string="Adjusted Amount", readonly=True, default=0,
                                   track_visibility='onchange', states={'draft': [('readonly', False)]})
    return_ids = fields.One2many('vendor.security.return.line', 'vsd_id',
                                 string='Security Return Lines')
    state = fields.Selection([
        ('draft', "Pending"),
        ('done', "Closed")], default='draft', string="Status",
        track_visibility='onchange')


