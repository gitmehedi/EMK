# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Analytic structure, for OpenERP
#    Copyright (C) 2016 XCG Consulting (www.xcg-consulting.fr)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
from openerp.addons.analytic_structure.MetaAnalytic import MetaAnalytic

NO_SEQUENCE_ERROR = _(
    "Please define sequence on the journal related to this invoice."
)
NO_INV_LINES_ERROR = _(
    "Please create some invoice lines."
)
INVOICE_AMOUNT_ERROR = _(
    "Cannot create the invoice.\n"
    "The related payment term is probably misconfigured "
    "as it gives a computed amount greater than the "
    "total invoiced amount. In order to avoid rounding "
    "issues, the latest line of your payment term must "
    "be of type 'balance'."
)
INV_AMOUNT_ERROR = _(
    "Please verify the price of the invoice!\n"
    "The encoded total does not match the computed total."
)
INV_PAYMENT_ERROR = _(
    "Cannot create the invoice.\n"
    "The related payment term is probably misconfigured "
    "as it gives a computed amount greater than the "
    "total invoiced amount. In order to avoid rounding "
    "issues, the latest line of your payment term must "
    "be of type 'balance'."
)
INV_JOURNAL_ERROR = _(
    "You cannot create an invoice on a centralized "
    "journal. Uncheck the centralized counterpart "
    "box in the related journal from the configuration menu."
)


class account_invoice_line(models.Model):
    __metaclass__ = MetaAnalytic
    _inherit = 'account.invoice.line'

    _analytic = 'account_invoice_line'

    def move_line_get_item(self, cr, uid, line, context=None):
        """Override this function to include analytic fields in generated
        move-line entries.
        """
        res = super(account_invoice_line, self).move_line_get_item(
            cr, uid, line, context
        )
        res.update(self.pool['analytic.structure'].extract_values(
            cr, uid, line, 'account_move_line', context=context
        ))
        return res


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(
            line, part, date)
        res.update(self.env['analytic.structure'].extract_values(
            line, 'account_invoice_line',
            dest_model='account_move_line',
            context=self._context
        ))
        return res

    @staticmethod
    def _get_object_reference(invoice):
        """Set the move object reference to account_invoice"""
        return 'account.invoice,%s' % invoice.id

    @api.multi
    def action_move_create(self):
        """Creates invoice related analytics and financial move lines
        Add reference to the invoice on the move.
        Note: This method duplicates code from the original
              implementation defined in the account module.
        """

        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise ValidationError(_(NO_SEQUENCE_ERROR))
            if not inv.invoice_line:
                raise ValidationError(_(NO_INV_LINES_ERROR))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({
                    'date_invoice': fields.Date.context_today(self)
                })
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv)
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if (
                self.env['res.users'].has_group(
                    'account.group_supplier_inv_check_total')
            ):
                if (
                    inv.type in ('in_invoice', 'in_refund') and
                    abs(inv.check_total - inv.amount_total) >=
                    (inv.currency_id.rounding / 2.0)
                ):
                    raise ValidationError(_(INV_AMOUNT_ERROR))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise ValidationError(_(INV_PAYMENT_ERROR))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other
            # lines amount
            total, total_currency, iml = (
                inv.with_context(ctx).compute_invoice_totals(
                    company_currency, ref, iml)
            )

            name = inv.name or inv.supplier_invoice_number or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(
                    total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = (
                            company_currency.with_context(ctx).compute(
                                t[1], inv.currency_id)
                        )
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                        })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(
                inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date))
                    for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise ValidationError(_(INV_JOURNAL_ERROR))

            line = inv.finalize_invoice_move_lines(line)

            if (
                inv.type in ('in_invoice', 'in_refund') and
                inv.supplier_invoice_number
            ):
                # Use the reference of this invoice as the reference of
                # generated account_move_object
                move_ref = inv.supplier_invoice_number
            else:
                move_ref = inv.reference or inv.name

            move_vals = {
                'ref': move_ref,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
                'object_reference': self._get_object_reference(inv),
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
                }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get
            # the same account move reference when creating the same invoice
            # after a cancelled one:
            move.post()
        self._log_event()
        return True

