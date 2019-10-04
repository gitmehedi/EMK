from odoo import models, fields, api, _


class Banks(models.Model):
    _name = 'res.bank'
    _order = 'name desc'
    _inherit = ['res.bank', 'mail.thread']

    name = fields.Char(track_visibility='onchange', size=200)
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state = fields.Many2one(track_visibility='onchange')
    country = fields.Many2one(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    bic = fields.Char(track_visibility='onchange', size=10)

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)

    @api.onchange("name", "bic")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.bic:
            self.bic = self.bic.strip()
