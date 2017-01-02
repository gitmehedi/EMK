# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import Warning


class product_product(models.Model):
    _inherit = "product.product"

    @api.one
    @api.constrains('company_id','active')
    def check_unique_company_and_default_code(self):
        print "-----------------", self.company_id, self.active
        if self.active and self.company_id:
            filters = [('company_id', '=', self.company_id.id),
                       ('active', '=', True)]
            prod_ids = self.search(filters)
            if len(prod_ids) > 1:
                raise Warning(_('There can not be two active products with same company.'))

