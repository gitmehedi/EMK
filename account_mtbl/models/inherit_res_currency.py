from odoo import models, fields, api, _


class Currency(models.Model):
    _name = 'res.currency'
    _order = 'name desc'
    _inherit = ['res.currency', 'mail.thread']

    name = fields.Char(string='Currency', size=3, required=True, help="Currency Code (ISO 4217)",
                       track_visibility='onchange')
    symbol = fields.Char(help="Currency sign, to be used when printing amounts.", required=True,
                         track_visibility='onchange')
    position = fields.Selection([('after', 'After Amount'), ('before', 'Before Amount')], default='after',
                                string='Symbol Position', track_visibility='onchange',
                                help="Determines where the currency symbol should be placed after or before the amount.")
    active = fields.Boolean(default=True, track_visibility='onchange')
    code = fields.Char('Code', required=True, size=3, track_visibility='onchange')
    rounding = fields.Float(string='Rounding Factor', digits=(12, 6), default=0.01, track_visibility='onchange')

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()
