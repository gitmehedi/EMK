from odoo import models, fields, api, _
from odoo import exceptions

class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['account.account', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange', size=8)
    parent_id = fields.Many2one(track_visibility='onchange')
    user_type_id = fields.Many2one(track_visibility='onchange')
    deprecated = fields.Boolean(track_visibility='onchange')
    reconcile = fields.Boolean(track_visibility='onchange')
    level_size = fields.Integer(related='level_id.size', )

    level_id = fields.Many2one('account.account.level', ondelete='restrict', string='Level', required=True,
                               track_visibility='onchange')

    @api.constrains('code')
    def _check_numeric_constrain(self):
        if self.code and not self.code.isdigit():
            raise exceptions.Warning(_('[Format Error] Code must be numeric!'))
        if self.level_id.size != len(self.code):
            raise exceptions.Warning(_('[Value Error] Code must be {0} digit!'.format(self.level_id.size)))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters_name = [['name', '=ilike', self.name.strip()]]
            name = self.search(filters_name)
            if len(name) > 1:
                raise exceptions.Warning(_('[Unique Error] Name must be unique!'))

    @api.onchange("level_id")
    def onchange_levels(self):
        if self.level_id:
            res = {}
            self.parent_id = 0
            parents = self.search([('level_id', '=', self.level_id.parent_id.id)])
            res['domain'] = {
                'parent_id': [('id', 'in', parents.ids),('internal_type','=','view')],
            }
            return res

    @api.onchange("code")
    def onchange_strips(self):
        if self.code:
            filter = str(self.code.strip()).upper()
            if self.level_size == 1:
                code = filter[:self.level_size]
            else:
                code = self.parent_id.code + filter

            self.code = code[:self.level_id.size]

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
