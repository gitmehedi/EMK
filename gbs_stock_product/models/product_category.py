# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.addons.opa_utility.helper.utility import Utility,Message
from odoo.exceptions import UserError, ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char('Code', required=True, help='This fields Code,...')
    company_id = fields.Many2one('res.company', 'Company')

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip())])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))



    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid,                                                                                                'product.category',
                                                                                                 context=c),
    }

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the product category group must be unique!')
    ]

    def _generate_categories(self, categories, category_id):
        categories.append(category_id)
        for cat in self.search([('parent_id', '=', category_id)]):
            categories = self._generate_categories(categories, cat.id)

        return categories

    def get_categories(self, category_id):
        categories = []
        categories = self._generate_categories(categories, category_id)

        return categories

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
