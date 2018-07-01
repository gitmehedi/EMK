from odoo import api, fields, models
from odoo.exceptions import UserError
import time


class ProductSalePriceHistiryLine(models.Model):
    _name = 'product.sale.history.line'
    _description = "Sale Price History"
    _rec_name = 'product_id'
    _order = "approve_price_date desc"

    product_id = fields.Many2one('product.product', string="Product", required=True, domain=[('sale_ok', '=', True)],readonly=True)
    list_price = fields.Float(string='Old Price', readonly=True)
    new_price = fields.Float(string='Price', required=True,readonly=True)
    approve_price_date = fields.Date(string='Approved Date',readonly=True)
    effective_price_date = fields.Date(string='Effective Date',readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)
    product_package_mode = fields.Many2one('product.packaging.mode', string= 'Packaging Mode', readonly=True)
    category_id = fields.Many2one(string='UoM Category',related="uom_id.category_id",store=True)
    uom_id = fields.Many2one('product.uom', string="UoM", readonly=True)

    @api.multi
    def unlink(self):
        raise UserError('You can not delete Price from here')
        return super(ProductSalePriceHistiryLine, self).unlink()


    @api.model
    def pull_automation(self):
        current_date = time.strftime("%m/%d/%Y")
        vals = {}

        price_list_pool = self.env['product.sales.pricelist'].search(
            [('state', '=', 'validate'), ('effective_date', '=', current_date)])

        for price_pool in price_list_pool:
            price_history_pool = self.env['product.sale.history.line'].search([('product_id', '=', price_pool.product_id.ids),
                                                                               ('currency_id', '=', price_pool.currency_id.id),
                                                                               ('product_package_mode', '=', price_pool.product_package_mode.id),
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

                price_history_pool.create(vals)
            else:
                price_history_pool.write({'product_id':price_pool.product_id.id, 'approve_price_date':price_pool.effective_date,
                                          'new_price':price_pool.new_price})

            #Update Products Sales Price also
            product_pool = self.env['product.product'].search([('id', '=', price_pool.product_id.ids)])

            product_pool.write({'list_price': price_pool.new_price, 'fix_price':price_pool.new_price})

