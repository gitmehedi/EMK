from odoo import api, fields, models
import time

import logging

_logger = logging.getLogger(__name__)


class InheritProductProduct(models.Model):
    _inherit = 'product.product'

    variant_new_price = fields.Float(string='New Price')

    @api.model
    def pull_automation(self):

        print "-------------------Updating Product variants price automatically rabbi--------------------------"

        current_date = time.strftime("%m/%d/%Y")

        price_list_pool = self.env['product.sales.pricelist'].search(
            [('state', '=', 'validate'), ('effective_date', '=', current_date)])

        for price_pool in price_list_pool:
            product_pool = self.env['product.product'].search(
                ([('attribute_value_ids', '=', price_pool.product_id.attribute_value_ids.ids)]))


            product_pool.write({'variant_new_price': price_pool.new_price})

        # for data_pull in self:
        #     try:
        #         data_pull.update_product_price()
        #     except Exception as e:
        #         self.env.cr.commit()
        #         _logger.error(e[0])
        #     finally:
        #         self.env.cr.commit()

