from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['account.account', 'mail.thread']

    name = fields.Char(track_visibility='onchange', size=50)
    code = fields.Char(track_visibility='onchange', size=8)
    parent_id = fields.Many2one(track_visibility='onchange')
    user_type_id = fields.Many2one(track_visibility='onchange')
    deprecated = fields.Boolean(track_visibility='onchange')
    reconcile = fields.Boolean(track_visibility='onchange')

    @api.constrains('code')
    def _check_numeric_constrain(self):
        if self.code and not self.code.isdigit():
            raise Warning('[Format Error] Code must be numeric!')
        if len(self.code) != 8:
            raise Warning('[Format Error] Code must be 8 digit!')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters_name = [['name', '=ilike', self.name.strip()]]
            name = self.search(filters_name)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("code", "name")
    def onchange_strips(self):
        if self.code:
            self.code = str(self.code.strip()).upper()
        if self.name:
            self.name = str(self.name.strip()).upper()

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)


class AccountAccountTag(models.Model):
    _inherit = 'account.account.tag'

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters_name = [['name', '=ilike', self.name.strip()]]
            name = self.search(filters_name)
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
