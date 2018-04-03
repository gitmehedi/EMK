# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class product_category(models.Model):
    _inherit = 'product.category'

    code = fields.Char('Code', required=True, help='This fields Code,...')
    company_id = fields.Many2one('res.company', 'Company')

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid,
                                                                                                 'product.category',
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
