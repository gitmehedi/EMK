from odoo import models, fields, api, _


class AccountAccountType(models.Model):
    _name = 'account.account.type'
    _order = 'name desc'
    _inherit = ['account.account.type', 'mail.thread']

    name = fields.Char(track_visibility='onchange', size=50)
    include_initial_balance = fields.Boolean(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    note = fields.Text(track_visibility='onchange', size=500)

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)
