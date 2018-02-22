from odoo import api, exceptions, fields, models
import operator, math
import locale

class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_accounting_cheque_received.report_money_receipt'
    
    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['accounting.cheque.received']
        docs = payslip_run_pool.browse(docids[0])
        data = {}

        account_conf_pool = self.env['account.config.settings'].search([], order='id desc', limit=1)

        seq = account_conf_pool.money_receipt_seq_id.next_by_code('account.money.receipt') or '/'

        data['sale_order_id'] = docs.sale_order_id.name
        data['partner_id'] = docs.partner_id.name
        data['cheque_amount'] = docs.cheque_amount
        data['is_cheque_payment'] = docs.is_cheque_payment
        data['date_on_cheque'] = docs.date_on_cheque
        data['bank_name'] = docs.bank_name.name
        data['branch_name'] = docs.branch_name
        data['company_id'] = docs.company_id.name
        data['date_on_cheque'] = docs.date_on_cheque
        data['mr_sl_no'] = seq

        locale.setlocale(locale.LC_ALL, 'bn_BD.UTF-8')
        thousand_separated_total_sum = locale.currency(docs.cheque_amount, grouping=True)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'accounting.cheque.received',
            'amount_to_words': self.env['res.currency'].amount_to_word(float(docs.cheque_amount)),
            'thousand_separated_total_sum': thousand_separated_total_sum,
            'data': data,
        }
        
        return self.env['report'].render('gbs_accounting_cheque_received.report_money_receipt', docargs)
    