# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning


class product_template(models.Model):
    _inherit = 'product.template'

    @api.one
    @api.constrains('name')
    def check_unique_company_and_default_code(self):
         
        if self.name and self.company_id:
            filters = [['company_id', '=', self.company_id.id],
                       ['name', '=ilike', self.name]]
            prod_ids = self.search(filters)
            if len(prod_ids) > 1:
                raise Warning(_('There can not be two active products with same company.'))

