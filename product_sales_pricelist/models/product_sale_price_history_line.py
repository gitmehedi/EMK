from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

import time


class ProductSalePriceHistiryLine(models.Model):
    _name = 'product.sale.history.line'
    _description = "Sale Price History"
    _rec_name = 'product_id'
    _order = "id DESC"

    product_id = fields.Many2one('product.product', string="Product", required=True, domain=[('sale_ok', '=', True)])
    list_price = fields.Float(string='Old Price',required=True,digits=dp.get_precision('Product Price'))
    new_price = fields.Float(string='Approved Price', required=True,digits=dp.get_precision('Product Price'))
    approve_price_date = fields.Date(string='Approved Date')
    #effective_price_date = fields.Date(string='Effective Date')
    currency_id = fields.Many2one('res.currency', string="Currency",required=True)
    product_package_mode = fields.Many2one('product.packaging.mode', string='Packaging Mode',required=True)
    category_id = fields.Many2one(string='UoM Category', related="uom_id.category_id")
    uom_id = fields.Many2one('product.uom', string="UoM",required=True)
    discount = fields.Float(string='Max Discount Limit')

    #-------------------------
    # country_id = fields.Many2one('res.country', string='Country')
    # terms_setup_id = fields.Many2one('terms.setup', string='Payment Days')
    # freight_mode = fields.Selection([('fob', 'FOB'),('c&f', 'C&F')], string='Freight Mode')


    @api.multi
    def unlink(self):
        raise UserError('You can not delete Price from here')
        return super(ProductSalePriceHistiryLine, self).unlink()


    @api.model
    def pull_automation(self):
        current_date = time.strftime("%m/%d/%Y")
        vals = {}

        price_list_pool = self.env['product.sales.pricelist'].search(
            [('state', '=', 'validate'), ('effective_date', '<=', current_date), ('is_process', '=',0)], order='effective_date ASC',)


        for price_pool in price_list_pool:
            price_history_pool = self.env['product.sale.history.line'].search([('product_id', '=', price_pool.product_id.ids),
                                                                               ('currency_id', '=', price_pool.currency_id.id),
                                                                               # ('country_id', '=',price_pool.country_id.id),
                                                                               # ('terms_setup_id','=',price_pool.terms_setup_id.id),
                                                                               ('product_package_mode', '=', price_pool.product_package_mode.id),
                                                                               #('freight_mode','=',price_pool.freight_mode),
                                                                               ('uom_id', '=', price_pool.uom_id.id)])


            if not price_history_pool:
                vals['product_id'] = price_pool.product_id.id
                vals['list_price'] = price_pool.list_price
                vals['new_price'] = price_pool.new_price
                vals['sale_price_history_id'] = price_pool.id
                vals['approve_price_date'] = price_pool.effective_date
                vals['currency_id'] = price_pool.currency_id.id
                vals['product_package_mode'] = price_pool.product_package_mode.id
                vals['uom_id'] = price_pool.uom_id.id
                vals['category_id'] = price_pool.uom_id.category_id.id
                vals['discount'] = price_pool.discount
                # vals['country_id'] = price_pool.country_id.id
                # vals['terms_setup_id'] = price_pool.terms_setup_id.id
                # vals['freight_mode'] = price_pool.freight_mode

                price_history_pool.create(vals)
            else:
                price_history_pool.write(
                    {
                        'product_id':price_pool.product_id.id,
                        'approve_price_date':price_pool.effective_date,
                        'new_price':price_pool.new_price,
                        'discount':price_pool.discount,
                        # 'country_id': price_pool.country_id.id,
                        # 'terms_setup_id':price_pool.terms_setup_id.id,
                        # 'freight_mode': price_pool.freight_mode
                    }
                )

            #Update Products Sales Price also
            product_pool = self.env['product.product'].search([('id', '=', price_pool.product_id.ids)])

            product_pool.write({'list_price': price_pool.new_price, 'fix_price':price_pool.new_price})

            product_pool.write({'discount': price_pool.discount})

            price_pool.write({'is_process': 1})