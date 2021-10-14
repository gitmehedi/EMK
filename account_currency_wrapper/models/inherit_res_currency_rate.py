from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    rate = fields.Float(digits=(12, 8))
    reverse_rate = fields.Float(string='Rate', digits=(12, 8), default=1.0)

    @api.constrains('reverse_rate')
    def constrains_reverse_rate(self):
        if self.reverse_rate == 0:
            raise ValidationError(_("Rate can't be Zero."))

    @api.onchange('reverse_rate')
    def onchange_reverse_rate(self):
        if self.reverse_rate != 0:
            self.rate = (1 / self.reverse_rate)
        else:
            self.rate = 1.0
