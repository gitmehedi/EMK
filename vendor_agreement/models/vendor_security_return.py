from odoo import api, fields, models, _


class VendorSecurityReturn(models.Model):
    _name = 'vendor.security.return'
    _inherit = ['mail.thread']
    _description = 'Vendor Security Return'
    _order = 'name desc'

    name = fields.Char(required=False, track_visibility='onchange', string='Name')
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', required=True,
                                 track_visibility='onchange',
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    vsd_ids = fields.Many2many('vendor.security.deposit', 'vendor_security_deposit_return_rel',
                               'return_id', 'deposit_id', string='Security Deposits',
                               readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange',
                          states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('vendor.security.return.line', 'return_id',
                               string='Security Return Lines')
    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('done', "Closed"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')


