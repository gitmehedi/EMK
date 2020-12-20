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

        ref = self.name + " of " + self.origin
        for stock_pack_products in self.pack_operation_product_ids:

            product = stock_pack_products.product_id
            amount = product.standard_price * stock_pack_products.product_qty

            debit_line_vals = {
                'name': product.name,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'account_id': product.cogs_account_id.id,
                'quantity': stock_pack_products.product_qty,
                'ref': ref,
                'partner_id': False,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'operating_unit_id': stock_pack_products.picking_id.operating_unit_id.id,

            }

            credit_line_vals = {
                'name': product.name,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'account_id': product.cogs_account_id.id,
                'quantity': stock_pack_products.product_qty,
                'ref': ref,
                'partner_id': False,
                'credit': amount if amount > 0 else 0,
                'debit': -amount if amount < 0 else 0,
                'operating_unit_id': stock_pack_products.picking_id.operating_unit_id.id,

            }

            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

            AccountMove = self.env['account.move']
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            journal_id = stock_pack_products.product_id.categ_id.property_stock_journal.id

            new_account_move = AccountMove.create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref})
            new_account_move.post()

            # stock_pack_products.product_id.categ_id.property_stock_valuation_account_id.name
            #
            # stock_pack_products.product_id.cogs_account_id
            #
            # stock_pack_products.product_id.standard_price
            #
            # stock_pack_products.product_qty
            #
            # stock_pack_products.picking_id.operating_unit_id