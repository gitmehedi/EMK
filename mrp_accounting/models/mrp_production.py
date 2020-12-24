# imports of odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        # Check Precondition
        self.validate()

        res = super(MrpProduction, self).button_mark_done()

        self.do_accounting()

        return res

    @api.multi
    def validate(self):
        is_valid = True

        message = ''
        categ_names_of_costing_method = set()
        categ_names_of_inventory_valuation = set()
        categ_names_of_stock_valuation_account = set()
        product_names_of_cogs_account = set()
        categ_name_of_stock_journal = None

        for move in self.move_raw_ids:
            if move.product_id.product_tmpl_id.categ_id.property_valuation != 'manual_periodic':
                is_valid = False
                categ_names_of_inventory_valuation.add(str(move.product_id.product_tmpl_id.categ_id.name))

            if not move.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id:
                is_valid = False
                categ_names_of_stock_valuation_account.add(str(move.product_id.product_tmpl_id.categ_id.name))

        for move in self.move_finished_ids:
            if move.product_id.product_tmpl_id.categ_id.property_cost_method != 'average':
                is_valid = False
                categ_names_of_costing_method.add(str(move.product_id.product_tmpl_id.categ_id.name))

            if move.product_id.product_tmpl_id.categ_id.property_valuation != 'manual_periodic':
                is_valid = False
                categ_names_of_inventory_valuation.add(str(move.product_id.product_tmpl_id.categ_id.name))

            if not move.product_id.product_tmpl_id.cogs_account_id.id:
                is_valid = False
                product_names_of_cogs_account.add(str(move.product_id.product_tmpl_id.name))

            if not move.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id:
                is_valid = False
                categ_names_of_stock_valuation_account.add(str(move.product_id.product_tmpl_id.categ_id.name))

        if not self.move_finished_ids[0].product_id.categ_id.property_stock_journal.id:
            is_valid = False
            categ_name_of_stock_journal = str(self.move_finished_ids[0].product_id.product_tmpl_id.categ_id.name)

        if categ_names_of_costing_method:
            message += _('- Costing Method must be "Average Price" for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(categ_names_of_costing_method))
        if categ_names_of_inventory_valuation:
            message += _('- Inventory Valuation must be "Periodic (manual)" for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(categ_names_of_inventory_valuation))
        if categ_names_of_stock_valuation_account:
            message += _('- Stock Valuation Account is missing for the mentioned Product category(s). '
                         'Which are %s.\n') % str(tuple(categ_names_of_stock_valuation_account))
        if product_names_of_cogs_account:
            message += _('- COGS Account is missing for the mentioned Product(s). '
                         'Which are %s.\n') % str(tuple(product_names_of_cogs_account))
        if categ_name_of_stock_journal:
            message += _('- Stock Journal is missing for "%s" product category.\n') % categ_name_of_stock_journal

        if not is_valid:
            message += _('Please Contact with Accounts Department. After that you are able to perform production.')
            raise ValidationError(_('Unable to perform production\n') + message)

    @api.multi
    def do_accounting(self):
        for order in self:
            moves_raw_ids = order.move_raw_ids.filtered(lambda x: x.state in ('done'))
            moves_finish_ids = order.move_finished_ids.filtered(lambda x: x.state in ('done'))
            tatal_raw_value, raw_meterial_acc = self._get_account_id_value_for_raw_goods(moves_raw_ids)

            finish_goods_acc = self._get_account_id_value_for_finish_goods(moves_finish_ids,tatal_raw_value)

            journal_id = moves_finish_ids[0].product_id.categ_id.property_stock_journal

            self.create_account_move_line(raw_meterial_acc, finish_goods_acc, journal_id[0].id, order.operating_unit_id.id)

            # moves_finish_ids.product_price_update_()

    def _get_account_id_value_for_raw_goods(self, moves_ids):
        raw_meterial_acc_id = {}
        tatal_raw_value  = 0
        for move in moves_ids:
            acc_id = move.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id

            total_price = move.product_uom_qty * move.price_unit
            tatal_raw_value += total_price

            if acc_id in raw_meterial_acc_id.keys():
                raw_meterial_acc_id[acc_id] = raw_meterial_acc_id[acc_id] + total_price
            else:
                raw_meterial_acc_id[acc_id] = total_price

        return tatal_raw_value, raw_meterial_acc_id

    def _get_account_id_value_for_finish_goods(self, moves_ids, tatal_raw_value):

        finish_acc_id = {}
        for move in moves_ids:
            acc_id = move.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id

            if acc_id in finish_acc_id.keys():
                finish_acc_id[acc_id] = finish_acc_id[acc_id] + tatal_raw_value
            else:
                finish_acc_id[acc_id] = tatal_raw_value

        return finish_acc_id

    def create_account_move_line(self, raw_meterial_acc, finish_goods_acc, journal_id, operating_unit_id):

        line_vals = []
        for key, value in finish_goods_acc.iteritems():
            debit_line_vals = {
                'name': self.name,
                'product_id': False,
                'quantity': False,
                'product_uom_id': False,
                'ref': False,
                'partner_id': False,
                'debit': value if value > 0 else 0,
                'credit': -value if value < 0 else 0,
                'account_id': key,
                'operating_unit_id': operating_unit_id
            }

            line_vals.append((0, 0, debit_line_vals))

        for key, value in raw_meterial_acc.iteritems():
            credit_line_vals = {
                'name': self.name,
                'product_id': False,
                'quantity': False,
                'product_uom_id': False,
                'ref': False,
                'partner_id': False,
                'credit': value if value > 0 else 0,
                'debit': -value if value < 0 else 0,
                'account_id': key,
                'operating_unit_id': operating_unit_id
            }
            line_vals.append((0, 0, credit_line_vals))
        AccountMove = self.env['account.move']
        if line_vals:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.create({
                'journal_id': journal_id,
                'line_ids': line_vals,
                'date': date,
                'ref': False,
                'operating_unit_id': operating_unit_id})
            new_account_move.post()