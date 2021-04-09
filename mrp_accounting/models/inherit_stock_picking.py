from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        # do default operation
        res = super(Picking, self).do_transfer()

        # cogs accounting region
        # check for doing cogs accounting
        if self.env.user.company_id.cogs_accounting:
            if self.operating_unit_id.code == 'SCCL-DF':
                if self.picking_type_id.code == 'outgoing':
                    self.validate()
                    # generate journal for cogs
                    self.do_cogs_accounting()

        # end region

        return res

    @api.multi
    def validate(self):
        is_valid = True

        message = ''

        costing_method_missing_categ_names = set()
        stock_valuation_account_missing_categ_names = set()
        raw_cogs_account_missing_product_names = set()
        packing_cogs_account_missing_product_names = set()
        cost_center_missing_product_names = set()

        for pack_operation_product in self.pack_operation_product_ids:
            if pack_operation_product.product_id.product_tmpl_id.categ_id.property_cost_method != 'average':
                is_valid = False
                costing_method_missing_categ_names.add(str(pack_operation_product.product_id.product_tmpl_id.categ_id.name))

            if not pack_operation_product.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id:
                is_valid = False
                stock_valuation_account_missing_categ_names.add(str(pack_operation_product.product_id.product_tmpl_id.categ_id.name))

            if not pack_operation_product.product_id.product_tmpl_id.raw_cogs_account_id.id:
                is_valid = False
                raw_cogs_account_missing_product_names.add(str(pack_operation_product.product_id.product_tmpl_id.name))

            if not pack_operation_product.product_id.product_tmpl_id.packing_cogs_account_id.id:
                is_valid = False
                packing_cogs_account_missing_product_names.add(str(pack_operation_product.product_id.product_tmpl_id.name))

            if not pack_operation_product.product_id.product_tmpl_id.cost_center_id.id:
                is_valid = False
                cost_center_missing_product_names.add(str(pack_operation_product.product_id.product_tmpl_id.name))

        if costing_method_missing_categ_names:
            message += _('- Costing Method must be "Average Price" for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(costing_method_missing_categ_names))
        if stock_valuation_account_missing_categ_names:
            message += _('- Stock Valuation Account is missing for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(stock_valuation_account_missing_categ_names))
        if raw_cogs_account_missing_product_names:
            message += _('- COGS Account (RM) is missing for the mentioned Product(s). '
                         'Which are %s.\n') % str(tuple(raw_cogs_account_missing_product_names))
        if packing_cogs_account_missing_product_names:
            message += _('- COGS Account (PM) is missing for the mentioned Product(s). '
                         'Which are %s.\n') % str(tuple(packing_cogs_account_missing_product_names))
        if cost_center_missing_product_names:
            message += _('- Cost Center is missing for the mentioned Product(s). '
                         'Which are %s.\n') % str(tuple(cost_center_missing_product_names))

        if not is_valid:
            raise ValidationError(message)

    @api.multi
    def do_cogs_accounting(self):

        ref = self.name + " of " + self.origin
        for stock_pack_products in self.pack_operation_product_ids:

            product = stock_pack_products.product_id
            # amount = product.standard_price * stock_pack_products.product_qty
            amount = product.standard_price * stock_pack_products.qty_done
            _logger.info("COGS Entry: Product Name:  " + str(product.display_name) + " Standard_price: " + str(
                product.standard_price) + " product_qty: " + str(stock_pack_products.qty_done))

            label = product.display_name + ";Rate:" + str(product.standard_price) + ";Qty:" + str(stock_pack_products.qty_done)
            debit_line_vals = {
                'name': label,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'account_id': product.product_tmpl_id.raw_cogs_account_id.id,
                'quantity': stock_pack_products.qty_done,
                'ref': ref,
                'partner_id': False,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'operating_unit_id': stock_pack_products.picking_id.operating_unit_id.id,
                'cost_center_id': product.product_tmpl_id.cost_center_id.id
            }

            credit_line_vals = {
                'name': label,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'account_id': product.categ_id.property_stock_valuation_account_id.id,
                'quantity': stock_pack_products.qty_done,
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
