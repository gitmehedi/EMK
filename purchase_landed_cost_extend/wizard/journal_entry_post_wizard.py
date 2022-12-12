from odoo import fields, api, models, _
from odoo.http import request
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import frozendict


class JournalEntryPost(models.TransientModel):
    _name = 'journal.entry.post.wizard'

    debit_account = fields.Many2one('account.account', 'Asset / Inventory GL', required=True)

    def _default_distribution(self):
        return self.env['purchase.cost.distribution'].browse(self.env.context.get('active_id'))

    distribution_id = fields.Many2one(
        'purchase.cost.distribution',
        default=lambda self: self._default_distribution(),
        required=True
    )

    def get_move_line_vals(self, name, date, journal_id, account_id, operating_unit_id, analytic_account_id,
                           debit, credit,
                           company_id):
        return {
            'name': name,
            'date': date,
            'journal_id': journal_id,
            'account_id': account_id,
            'operating_unit_id': operating_unit_id,
            'analytic_account_id': analytic_account_id,
            'debit': debit,
            'credit': credit,
            # 'company_id': company_id,
        }

    def post_entry(self):
        if not self.distribution_id.analytic_account:
            raise UserError('Analytic Account not found!')

        journal_id = self.env['account.journal'].sudo().search(
            [('code', '=', 'STJ'), ('company_id', '=', self.distribution_id.operating_unit_id.company_id.id)], limit=1)
        if not journal_id:
            raise UserError('Stock Journal not found!')
        lc_pad_account = self.env['ir.values'].get_default('account.config.settings', 'lc_pad_account')

        if not lc_pad_account:
            raise UserError(
                _(
                    "LC Goods In Transit Account not set. Please contact your system administrator for assistance."))

        move_lines = []

        expense_lines = self.env['purchase.cost.distribution.expense'].search(
            [('distribution', '=', self.distribution_id.id)])
        ref = ''
        for expense in expense_lines:
            ref = expense.ref
            credit_entry = self.get_move_line_vals(expense.ref, self.distribution_id.date, journal_id.id,
                                                   expense.account_id.id,
                                                   self.distribution_id.operating_unit_id.id,
                                                   self.distribution_id.analytic_account.id,
                                                   0,
                                                   expense.expense_amount,
                                                   self.distribution_id.operating_unit_id.company_id.id)
            move_lines.append((0, 0, credit_entry))

        credit_entry = self.get_move_line_vals(ref, self.distribution_id.date, journal_id.id,
                                               lc_pad_account,
                                               self.distribution_id.operating_unit_id.id,
                                               self.distribution_id.analytic_account.id,
                                               0,
                                               self.distribution_id.total_purchase,
                                               self.distribution_id.operating_unit_id.company_id.id)
        move_lines.append((0, 0, credit_entry))

        debit_entry = self.get_move_line_vals(ref, self.distribution_id.date, journal_id.id,
                                              self.debit_account.id,
                                              self.distribution_id.operating_unit_id.id,
                                              False,
                                              self.distribution_id.total_expense + self.distribution_id.total_purchase,
                                              0,
                                              self.distribution_id.operating_unit_id.company_id.id)

        move_lines.append((0, 0, debit_entry))
        vals = {
            'journal_id': journal_id.id,
            'operating_unit_id': self.distribution_id.operating_unit_id.id,
            'date': self.distribution_id.date,
            'company_id': self.distribution_id.operating_unit_id.company_id.id,
            'state': 'draft',
            'line_ids': move_lines,
            'narration': '',
            'ref': 'landed cost provision'
        }

        move = self.env['account.move'].create(vals)
        self.distribution_id.write({'account_move_id': move.id, 'debit_account': self.debit_account.id})

        ####UPDATE Product Cost
        context = dict(self.env.context)
        context.update({
            'datetime_of_price_history': self.distribution_id.date + ' ' + datetime.now().strftime("%H:%M:%S"),
            'operating_unit_id': self.distribution_id.operating_unit_id.id
        })
        self.distribution_id.env.context = frozendict(context)

        self.distribution_id.ensure_one()
        if self.distribution_id.cost_update_type != 'direct':
            return

        d = {}
        for line in self.distribution_id.cost_lines:
            product = line.move_id.product_id
            if product.cost_method != 'average':
                continue
            line.move_id.quant_ids._price_update(line.standard_price_new)
            d.setdefault(product, [])
            d[product].append(
                (line.move_id,
                 line.standard_price_new - line.standard_price_old, line.standard_price_new),
            )

        for product, vals_list in d.items():
            self.distribution_id._product_price_update(product, vals_list)
            for vals in vals_list:
                vals[0].product_price_update_after_done()
        self.distribution_id.state = 'done'
