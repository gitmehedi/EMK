# imports of odoo
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        # Check Precondition

        res = super(MrpProduction, self).button_mark_done()

        self.do_accounting()

        return res

    @api.multi
    def do_accounting(self):
        for order in self:
            moves_raw_ids = order.move_raw_ids.filtered(lambda x: x.state in ('done'))
            moves_finish_ids = order.move_finished_ids.filtered(lambda x: x.state in ('done'))
            raw_meterial_acc = self._get_account_id_value(moves_raw_ids)
            finish_goods_acc = self._get_account_id_value(moves_finish_ids)

            journal_id = moves_finish_ids[0].product_id.categ_id.property_stock_journal

            self.create_account_move_line(raw_meterial_acc, finish_goods_acc, journal_id[0].id)

    def _get_account_id_value(self, moves_ids):
        raw_meterial_acc_id = {}

        for move in moves_ids:
            acc_id = move.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id

            total_price = move.product_uom_qty * move.price_unit

            if acc_id in raw_meterial_acc_id.keys():
                raw_meterial_acc_id[acc_id] = raw_meterial_acc_id[acc_id] + total_price
            else:
                raw_meterial_acc_id[acc_id] = total_price

        return raw_meterial_acc_id

    def create_account_move_line(self, raw_meterial_acc, finish_goods_acc, journal_id):

        line_vals = []
        for key, value in finish_goods_acc.iteritems():
            credit_line_vals = {
                'name': self.name,
                'product_id': None,
                'quantity': None,
                'product_uom_id': None,
                'ref': None,
                'partner_id': 0,
                'debit': value if value > 0 else 0,
                'credit': -value if value < 0 else 0,
                'account_id': key
            }

            line_vals.append(credit_line_vals)

        for key, value in raw_meterial_acc.iteritems():
            credit_line_vals = {
                'name': self.name,
                'product_id': None,
                'quantity': None,
                'product_uom_id': None,
                'ref': None,
                'partner_id': 0,
                'credit': value if value > 0 else 0,
                'debit': -value if value < 0 else 0,
                'account_id': key
            }
            line_vals.append(credit_line_vals)

        AccountMove = self.env['account.move']
        if line_vals:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.create({
                'journal_id': journal_id,
                'line_ids': line_vals,
                'date': date,
                'ref': ""})
            new_account_move.post()