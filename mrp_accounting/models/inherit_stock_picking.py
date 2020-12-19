from odoo import models, fields, api,_
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()

        if self.location_dest_id.name == 'Customers':
            # Check Procondition
            self.do_COGS_accounting()
        return res

    @api.multi
    def do_COGS_accounting(self):
        for stock_pack_products in self.pack_operation_product_ids:
            print ("")
            # stock_pack_products.product_id.categ_id.property_stock_valuation_account_id.name
            #
            # stock_pack_products.product_id.cogs_account_id
            #
            # stock_pack_products.product_id.standard_price
            #
            # stock_pack_products.product_qty
            #
            # stock_pack_products.picking_id.operating_unit_id