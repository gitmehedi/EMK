from odoo import api, fields, models


class AccountLevel(models.Model):
    _name = 'account.account.level'
    _inherit = ['mail.thread']

    name = fields.Char(string='Layer Name', size=200, required=True, track_visibility='onchange')
    size = fields.Integer(string='Level Size', size=2, required=True, track_visibility='onchange')
    prefix = fields.Char(string='Prefix', track_visibility='onchange')
    parent_id = fields.Many2one('account.account.level', ondelete='restrict', string='Parent Name')
    is_visible = fields.Boolean(default=True)

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search([('name', '=ilike', self.name.strip())])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
