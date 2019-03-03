# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class SubOperatingUnit(models.Model):
    _name = 'sub.operating.unit'
    _inherit = ['mail.thread']
    _description = 'Sub Operating Unit'

    name = fields.Char('Name', required=True ,track_visibility='onchange')
    code = fields.Char('Code', required=True ,size=3,track_visibility='onchange')
    active = fields.Boolean('Active', default=True,track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Partner', required=True,track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,track_visibility='onchange',
                        default=lambda self:self.env['res.company']._company_default_get('account.account'))

    _sql_constraints = [
        ('code_company_sub_uniq', 'unique (code,company_id)',
         'Code of The Operating Unit Must be unique per company!'),
        ('name_company_sub_uniq', 'unique (name,company_id)',
         'Name of the Sub Operating Unit Must be unique per company!')
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name,code='COD')
        return super(SubOperatingUnit, self).copy(default)
