from odoo import models, fields, api, _


class BGLAccounts(models.Model):
    _name = 'bgl.accounts'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'BGL Accounts'

    name = fields.Char(string='Name', required=True, size=200,
                       track_visibility='onchange')
    code = fields.Char(string='Code', required=True, size=11,
                       track_visibility='onchange')
    active = fields.Boolean(string='Active', default=True,
                            track_visibility='onchange')
    note = fields.Text(string='Note', track_visibility='onchange')

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            code = self.search(
                [('code', '=ilike', self.code.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')
            if not self.code.isdigit():
                raise Warning('[Format Error] Code must be numeric!')
            if len(self.code) != 11:
                raise Warning('[Format Error] Code must be 11 digit!')

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)
