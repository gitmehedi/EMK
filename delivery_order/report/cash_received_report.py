from odoo import api, fields, models
from odoo.tools.misc import formatLang


class CashReceivedReport(models.AbstractModel):
    _name = 'report.delivery_order.report_individual_payslip'
    
    @api.model
    def render_html(self, docids, data=None):
        acc_payment_pool = self.env['account.payment']
        docs = acc_payment_pool.browse(docids[0])
        data = {}

        account_conf_pool = self.env['account.config.settings'].search([], order='id desc', limit=1)

        seq = account_conf_pool.money_receipt_seq_id.next_by_code('account.money.receipt') or '/'

        data['partner_id'] = docs.partner_id.name
        data['is_cash_payment'] = docs.is_cash_payment
        data['deposited_bank'] = docs.deposited_bank.name
        data['bank_branch'] = docs.bank_branch
        data['cheque_amount'] = docs.amount
        # data['sale_order_id'] = docs.sale_order_id.name
        data['payment_date'] = docs.payment_date
        data['mr_sl_no'] = seq
        data['company_id'] = docs.company_id.name
        data['currency_id'] = docs.currency_id.name

        amt_to_word = self.env['res.currency'].amount_to_word(float(docs.amount),True,data['currency_id'])

        thousand_separated_total_sum = formatLang(self.env, docs.amount)

        docargs = {
            'doc_model': 'account.payment',
            'thousand_separated_total_sum': thousand_separated_total_sum,
            'amount_to_words': amt_to_word,
            'data': data,
        }
        
        return self.env['report'].render('delivery_order.report_individual_payslip', docargs)