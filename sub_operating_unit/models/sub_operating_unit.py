# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SubOperatingUnit(models.Model):
    _name = 'sub.operating.unit'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Sub Operating Unit'

    name = fields.Char('Name', required=True, size=50, track_visibility='onchange')
    code = fields.Char('Code', required=True, size=3, track_visibility='onchange')
    active = fields.Boolean('Active', default=True, track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, track_visibility='onchange',
        default=lambda self: self.env['res.company']._company_default_get('account.account'))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

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
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name, code='COD')
        return super(SubOperatingUnit, self).copy(default)
