from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()

        if self.location_dest_id.name == 'Customers':
            # Check Procondition
            self.validate()

            self.do_COGS_accounting()
        return res

    @api.multi
    def validate(self):
        is_valid = True

        message = ''
        categ_names_of_costing_method = set()
        categ_names_of_stock_valuation_account = set()
        product_names_of_cogs_account = set()

        for pack_operation_product in self.pack_operation_product_ids:
            if pack_operation_product.product_id.product_tmpl_id.categ_id.property_cost_method != 'average':
                is_valid = False
                categ_names_of_costing_method.add(str(pack_operation_product.product_id.product_tmpl_id.categ_id.name))

            if not pack_operation_product.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id:
                is_valid = False
                categ_names_of_stock_valuation_account.add(str(pack_operation_product.product_id.product_tmpl_id.categ_id.name))

            if not pack_operation_product.product_id.product_tmpl_id.cogs_account_id.id:
                is_valid = False
                product_names_of_cogs_account.add(str(pack_operation_product.product_id.product_tmpl_id.name))

        if categ_names_of_costing_method:
            message += _('- Costing Method must be "Average Price" for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(categ_names_of_costing_method))
        if categ_names_of_stock_valuation_account:
            message += _('- Stock Valuation Account is missing for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(categ_names_of_stock_valuation_account))
        if product_names_of_cogs_account:
            message += _('- COGS Account is missing for the mentioned Product(s). '
                         'Which are %s.\n') % str(tuple(product_names_of_cogs_account))

        if not is_valid:
            raise ValidationError(message)

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
                'account_id': product.categ_id.property_stock_valuation_account_id.id,
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