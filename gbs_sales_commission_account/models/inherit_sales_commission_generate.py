from odoo import api, fields, models
import datetime
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError



class InheritSalesCommissionGenerate(models.Model):
    _inherit = 'sales.commission.generate'


    @api.multi
    def action_approve_sales_commission(self):

        company_id = self.env['res.company']._company_default_get('gbs_sales_commission_account')
        precision = self.env['decimal.precision'].precision_get('Payroll')

        line_ids = []
        for line in self.line_ids:
            for invoice_line in line.invoice_line_ids:
                for p_id in invoice_line.product_id:


                    debit_sum = 0.0
                    credit_sum = 0.0
                    date = datetime.datetime.today().strftime('%Y-%m-%d')

                    if not company_id.commission_journal:
                        raise UserError('Commission Journal is not set for company : %s' % company_id.display_name)


                    move_dict = {
                        'journal_id': company_id.commission_journal.id,
                        'date': date,
                    }

                    amount = invoice_line.commission_amount or -invoice_line.commission_amount

                    if float_is_zero(amount, precision_digits=precision):
                        continue

                    debit_account_id = p_id.product_tmpl_id.commission_expense
                    credit_account_id = line.partner_id.property_account_payable_id

                    if not debit_account_id:
                        raise UserError('Debit Account is not configured for: %s' % p_id.display_name)

                    if not credit_account_id:
                        raise UserError('Credit Account is not configured for Customer: %s' % line.partner_id.name)

                    if debit_account_id:
                        debit_line = (0, 0, {
                            'name': debit_account_id.name,
                            # 'operating_unit_id': r[2]['operating_unit_id'],
                            'product_id': p_id.id,
                            'account_id': debit_account_id.id,
                            'journal_id': company_id.commission_journal.id,
                            'date': date,
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                        line_ids.append(debit_line)
                        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']


                        if credit_account_id:
                            credit_line = (0, 0, {
                                'name': credit_account_id.name,
                                'partner_id': line.partner_id.id,
                                'product_id': p_id.id,
                                 #'operating_unit_id': a
                                'account_id': credit_account_id.id,
                                'journal_id': company_id.commission_journal.id,
                                'date': date,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                            })

                            line_ids.append(credit_line)
                            credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']


        move_dict['line_ids'] = line_ids
        move = line.env['account.move'].create(move_dict)

        move.post()

        res = super(InheritSalesCommissionGenerate, self).action_approve_sales_commission()

