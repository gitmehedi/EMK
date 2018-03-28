# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PurchaseProductionTerms(models.Model):
    _name = 'purchase.production.terms'
    _description = 'Contains production terms named CM, FOB'
    _order = 'id desc'

    name = fields.Char(string='Title', required=True)
    code = fields.Char(string='Code', required=True)
    status = fields.Boolean(string='Status', default=True)

    @api.constrains('name')
    def _unique_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Product Terms should not be duplicate.'))
