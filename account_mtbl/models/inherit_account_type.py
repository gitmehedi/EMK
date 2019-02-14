from odoo import models, fields, api, _

class AccountAccountType(models.Model):
    _name = 'account.account.type'
    _inherit = ['account.account.type','mail.thread']

    name = fields.Char(track_visibility='onchange')
    include_initial_balance = fields.Boolean(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    note = fields.Text(track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters_name = [['name', '=ilike', self.name]]
            name = self.search(filters_name)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
