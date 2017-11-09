from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class InheritProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def pull_automation(self):
        print "-------------------calling data pulling automatically rabbi--------------------------"
        for data_pull in self:
            try:
                data_pull.update_product_price()
            except Exception as e:
                self.env.cr.commit()
                _logger.error(e[0])
            finally:
                self.env.cr.commit()

    def update_product_price(self):
        print '----------------------------------------'
