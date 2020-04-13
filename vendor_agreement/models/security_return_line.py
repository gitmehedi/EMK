from odoo import api, fields, models, _


class VendorSecurityReturn(models.Model):
    _name = 'vendor.security.return.line'
    _description = 'Vendor Security Return Line'
    _order = 'id desc'

    return_id = fields.Many2one('vendor.security.return', string="Vendor Security Return Id")
    vsd_id = fields.Many2one('vendor.security.deposit', string="Vendor Security Deposit Id")
    date = fields.Datetime('Return Date')
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange')
