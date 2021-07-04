# imports of odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, index=True, ondelete='restrict',
                              copy=False, help="Link to the automatically generated Journal Items.")

    @api.multi
    def action_unbuild(self):
        self.ensure_one()
        res = super(MrpUnbuild, self).action_unbuild()
        self.do_accounting()

        return res

    @api.multi
    def do_accounting(self):
        produce_moves = self.produce_line_ids.filtered(lambda x: x.state == 'done')
        consume_moves = self.consume_line_ids.filtered(lambda x: x.state == 'done')

        journal_id = consume_moves[0].product_id.categ_id.property_stock_journal.id

        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        move = self.env['account.move'].create({'journal_id': journal_id,
                                                'date': self.date_unbuild,
                                                'operating_unit_id': self.operating_unit_id.id,
                                                'company_id': self.bom_id.company_id.id})

        # credit part
        account_id = consume_moves[0].product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id
        credit = sum(sm.product_uom_qty * sm.price_unit for sm in produce_moves)
        credit_aml_dict = self._prepare_credit_move_line(move.id, account_id, credit)
        aml_obj.create(credit_aml_dict)

        # debit part
        for sm in produce_moves:
            account_id = sm.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id
            debit = sm.product_uom_qty * sm.price_unit

            aml = move.line_ids.filtered(lambda x: x.account_id.id == account_id)
            if aml:
                aml.debit += debit
            else:
                debit_aml_dict = self._prepare_debit_move_line(move.id, account_id, debit)
                aml_obj.create(debit_aml_dict)

        # post journal entries
        move.post()
        self.write({'move_id': move.id})

    def _prepare_credit_move_line(self, move_id, account_id, credit):
        vals = {
            'name': self.name,
            'date_maturity': self.date_unbuild,
            'credit': credit,
            'debit': False,
            'account_id': account_id,
            'operating_unit_id': self.operating_unit_id.id,
            'move_id': move_id
        }
        return vals

    def _prepare_debit_move_line(self, move_id, account_id, debit):
        vals = {
            'name': self.name,
            'date_maturity': self.date_unbuild,
            'credit': False,
            'debit': debit,
            'account_id': account_id,
            'operating_unit_id': self.operating_unit_id.id,
            'move_id': move_id
        }
        return vals

