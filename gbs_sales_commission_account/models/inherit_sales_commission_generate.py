from odoo import api, fields, models
import datetime
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError



class InheritSalesCommissionGenerate(models.Model):
    _inherit = 'sales.commission.generate'

    def _prepare_lines_for_invoices_products(self):
        res = []
        product_list = []
        total_commission = 0
        prod_line = {}

        for sc in self:
            for line in sc.line_ids:
                for comm_line in line.invoice_line_ids:
                    for inv_line in comm_line.invoice_id.invoice_line_ids:
                        new_prod = True
                        for prod in product_list:
                            if inv_line.product_id.id == prod['product_id']:
                                  #  and inv_line.operating_unit_id.id == prod['operating_unit_id']:
                                new_prod = False
                                total_commission += inv_line.invoice_id.generated_commission_amount
                                # prod_line = {
                                #     'product_id': inv_line.product_id.id,
                                #     'generated_commission_amount': total_commission
                                # }

                        if new_prod:
                            prod_line = {
                                'product_id': inv_line.product_id.id,
                                'partner_id': inv_line.partner_id.id,
                               # 'operating_unit_id': inv_line.operating_unit_id.id,
                                'generated_commission_amount': inv_line.invoice_id.generated_commission_amount
                            }

                        product_list.append(prod_line)

            print 'total comm', total_commission
            for prod in product_list:
                res.append([0, 0, prod])

        return res


    @api.multi
    def action_approve_sales_commission(self):
        res = super(InheritSalesCommissionGenerate, self).action_approve_sales_commission()

        precision = self.env['decimal.precision'].precision_get('Payroll')

        result = self._prepare_lines_for_invoices_products()

        company_id = self.env['res.company']._company_default_get('gbs_sales_commission_account')

        for slip in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = datetime.datetime.today().strftime('%Y-%m-%d')

            move_dict = {
                'journal_id': company_id.commission_journal.id,
                'date': date,
            }

            for r in result:
                product_pool = slip.env['product.product'].search([('id','=',r[2]['product_id'])])

                amount = r[2]['generated_commission_amount'] or -r[2]['generated_commission_amount']
                if float_is_zero(amount, precision_digits=precision):
                    continue

                debit_account_id = product_pool.product_tmpl_id.commission_expense
                credit_account_id = company_id.commission_journal.default_credit_account_id  # line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': debit_account_id.name,  # line.name,
                        'partner_id': r[2]['partner_id'],
                        #'operating_unit_id': r[2]['operating_unit_id'],
                        'account_id': debit_account_id.id,
                        'journal_id': company_id.commission_journal.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        # 'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        # 'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': credit_account_id.name,
                        'partner_id': r[2]['partner_id'],
                        #'operating_unit_id': r[2]['operating_unit_id'],
                        'account_id': credit_account_id.id,
                        'journal_id': company_id.commission_journal.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        # 'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        # 'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })

                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = company_id.commission_journal.default_credit_account_id.id
                    if not acc_id:
                        raise UserError(
                            ('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                company_id.commission_journal.name))
                    adjust_credit = (0, 0, {
                        'name': ('Adjustment Entry'),
                        'partner_id': False,
                        'account_id': acc_id,
                        'journal_id': company_id.commission_journal.id,
                        'date': date,
                        'debit': 0.0,
                        'credit': debit_sum - credit_sum,
                    })
                    line_ids.append(adjust_credit)

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = product_pool.product_tmpl_id.commission_expense.id
                    if not acc_id:
                        raise UserError(
                            ('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                company_id.commission_journal.name))
                    adjust_debit = (0, 0, {
                        'name': ('Adjustment Entry'),
                        'partner_id': False,
                        'account_id': acc_id,
                        'journal_id': company_id.commission_journal.id,
                        'date': date,
                        'debit': credit_sum - debit_sum,
                        'credit': 0.0,
                    })
                    line_ids.append(adjust_debit)



        print 'credit sum --- ', credit_sum
        print 'debit sum --- ', debit_sum


        move_dict['line_ids'] = line_ids
        move = slip.env['account.move'].create(move_dict)
        #slip.write({'move_id': move.id, 'date': date})
        move.post()

        return res
