from odoo import models, fields, api, _

class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['account.account','mail.thread']

    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    user_type_id = fields.Many2one(track_visibility='onchange')
    deprecated = fields.Boolean(track_visibility='onchange')
    reconcile = fields.Boolean(track_visibility='onchange')

    @api.constrains('code')
    def _check_numeric_constrain(self):
        for i in self:
            if i.code and not i.code.isdigit():
                raise Warning('[Format Error] Code must be numeric!')

    @api.onchange('name')
    def set_caps(self):
        for i in self:
            if i.name:
                i.name = str(i.name).upper()


