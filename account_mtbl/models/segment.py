from odoo import models, fields, api, _


class Segment(models.Model):
    _name = 'segment'
    _inherit = ['mail.thread']
    _order = 'code desc'
    _description = 'Segment'

    name = fields.Char('Name', required=True, size=50, track_visibility='onchange')
    code = fields.Char('Code', required=True, size=1, track_visibility='onchange')
    active = fields.Boolean('Active', default=True, track_visibility='onchange')

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            code = self.search(
                [('code', '=ilike', self.code.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')
            if not self.code.isdigit():
                raise Warning(_('[Format Error] Code must be numeric!'))

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
