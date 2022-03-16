from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    raw_mushok_amount = fields.Float(string='Mushok Value', digits=(16, 4), default=0.0, track_visibility='onchange', help='For Mushok-6.3')
    raw_vds_amount = fields.Float(string='VDS Authority Value', digits=(16, 4), default=0.0, track_visibility='onchange', help='For VDS Authority')

    mushok_amount = fields.Float(string='Mushok Value', digits=(16, 4), default=0.0, track_visibility='onchange', help='For Mushok-6.3')
    vds_amount = fields.Float(string='VDS Authority Value', digits=(16, 4), default=0.0, track_visibility='onchange', help='For VDS Authority')

    @api.onchange('raw_mushok_amount', 'raw_vds_amount', 'is_reverse')
    def onchange_raw_mushok_amount(self):
        self.mushok_amount = (self.raw_mushok_amount * -1) if self.is_reverse else self.raw_mushok_amount
        self.vds_amount = (self.raw_vds_amount * -1) if self.is_reverse else self.raw_vds_amount
