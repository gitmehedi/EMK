from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'mail.thread']
    _order = 'code desc'
    _description = 'Cost Centre'

    name = fields.Char('Name', required=True, size=50, track_visibility='onchange')
    code = fields.Char('Code', required=True, size=3, track_visibility='onchange')
    operating_unit_ids = fields.Many2many(string='Branch', track_visibility='onchange')

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            filters_name = [['name', '=ilike', self.name]]
            filters_code = [['code', '=ilike', self.code]]
            name = self.search(filters_name)
            code = self.search(filters_code)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            elif len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')

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


class AccountAnalyticTag(models.Model):
    _name = 'account.analytic.tag'
    _inherit = ['account.analytic.tag', 'mail.thread']
    _order = 'id desc'
    _description = 'Cost Centre Tag'

    name = fields.Char('Name', required=True, size=50, track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search([['name', '=ilike', self.name]])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['account.analytic.line', 'mail.thread']
    _order = 'id desc'
    _description = 'Cost Centre Line'

    name = fields.Char(required=True, size=50, track_visibility='onchange')

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
