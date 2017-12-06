# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import odoo.addons.decimal_precision as dp


class ProductSalesPriceHistory(models.Model):
    """ Keep track of the ``product.template`` sales prices as they are changed. """
    _name = 'product.sales.price.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    company_id = fields.Many2one('res.company', string='Company',
        default=_get_default_company_id, required=True)
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', required=True)
    datetime = fields.Datetime('Date', default=fields.Datetime.now)
    lst_price = fields.Float('Sale Price', digits=dp.get_precision('Product Price'))


class ProductProduct(models.Model):
    _inherit = "product.product"

    lst_price = fields.Float('Sale Price', digits=dp.get_precision('Product Price'),
                             compute='_get_product_lst_price',
                             help="The sale price is managed from the product template. Click on the 'Variant Prices' button to set the extra attribute prices.")

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self.with_context(create_product_product=True)).create(vals)
        # When a unique variant is created from tmpl then the list price is set by _set_lst_price
        if not (self.env.context.get('create_from_tmpl') and len(product.product_tmpl_id.product_variant_ids) == 1):
            product._set_lst_price(vals.get('list_price') or 0.0)
        return product

    @api.multi
    def write(self, values):
        ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
        res = super(ProductProduct, self).write(values)
        if 'list_price' in values:
            self._set_lst_price(values['list_price'] or 0.0)
        return res

    @api.multi
    def _get_product_lst_price(self):
        # select
        # h.product_id, h.lst_price
        # from product_sales_price_history h
        # join(select
        # product_id, max(datetime) as datetime
        # from product_sales_price_history
        #     where
        # product_id in (12, 10)
        # group
        # by
        # product_id) t
        # on
        # h.product_id = t.product_id
        # and h.datetime = t.datetime
        history = self.env['product.sales.price.history'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('product_id', 'in', self.ids),
            ('datetime', '<=', fields.Datetime.now())], order='datetime desc,id desc', limit=1)
        return history.lst_price or 0.0

    @api.multi
    def _set_lst_price(self, value):
        ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
        PriceHistory = self.env['product.sales.price.history']
        for product in self:
            PriceHistory.create({
                'product_id': product.id,
                'lst_price': value,
                'company_id': self._context.get('force_company', self.env.user.company_id.id),
            })

    @api.multi
    def get_history_price(self, company_id, date=None):
        history = self.env['product.sales.price.history'].search([
            ('company_id', '=', company_id),
            ('product_id', 'in', self.ids),
            ('datetime', '<=', date or fields.Datetime.now())], order='datetime desc,id desc', limit=1)
        return history.lst_price or 0.0
