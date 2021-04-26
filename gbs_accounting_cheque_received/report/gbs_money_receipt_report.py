from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_accounting_cheque_received.report_money_receipt'
    
    @api.model
    def render_html(self, docids, data=None):
        cheque_rcv_pool = self.env['accounting.cheque.received']
        docs = cheque_rcv_pool.browse(docids[0])
        data = {}

        account_conf_pool = self.env['account.config.settings'].search([], order='id desc', limit=1)

        seq = account_conf_pool.money_receipt_seq_id.next_by_code('account.money.receipt') or '/'

        if docs.journal_id.currency_id:
            currency = docs.journal_id.currency_id
        else:
            currency = docs.company_id.currency_id

        data['partner_id'] = docs.partner_id.name
        data['cheque_amount'] = docs.cheque_amount
        data['is_cheque_payment'] = docs.is_cheque_payment
        data['date_on_cheque'] = docs.date_on_cheque
        data['bank_name'] = docs.bank_name.name
        data['branch_name'] = docs.branch_name
        data['company_id'] = docs.company_id.name
        data['date_on_cheque'] = docs.date_on_cheque
        data['mr_sl_no'] = seq
        data['currency'] = currency.name
        data['cheque_no'] = docs.cheque_no

        thousand_separated_total_sum = formatLang(self.env, docs.cheque_amount)

        amt_to_word = self.env['res.currency'].amount_to_word(float(docs.cheque_amount),True,data['currency'])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'accounting.cheque.received',
            'amount_to_words': amt_to_word,
            'thousand_separated_total_sum': thousand_separated_total_sum,
            'data': data,
        }
        
        return self.env['report'].render('gbs_accounting_cheque_received.report_money_receipt', docargs)
