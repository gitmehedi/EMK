from odoo import api, models, fields
from odoo.tools.misc import formatLang


class GBSVoucherReport(models.AbstractModel):
    _name = 'report.gbs_voucher.voucher_report'

    @api.multi
    def render_html(self, docids, data=None):
        # retrieve account move object
        am_obj = self.env['account.move'].browse(docids[0])
        # set report title
        if am_obj.journal_id.type == 'cash':
            report_title = 'Cash Payment Voucher'
        elif am_obj.journal_id.type == 'bank':
            report_title = 'Bank Payment Voucher'
        elif am_obj.journal_id.type == 'general':
            report_title = 'Miscellaneous Voucher'
        else:
            report_title = 'Journal Voucher'

        report_data = {}
        report_data['name'] = am_obj.name
        report_data['ref'] = am_obj.ref
        report_data['date'] = am_obj.date
        report_data['narration'] = am_obj.narration
        report_data['amount'] = am_obj.amount
        report_data['lines'] = []

        for line in am_obj.line_ids:
            dict_obj = {}
            dict_obj['account_name'] = line.account_id.display_name
            dict_obj['analytic_account_name'] = line.analytic_account_id.display_name
            aat_name = ''
            for tag in line.analytic_account_id.tag_ids:
                aat_name += tag.display_name + ', '
            dict_obj['analytic_account_tag_names'] = aat_name[:len(aat_name)-2] if len(aat_name) > 0 else False
            dict_obj['department_name'] = line.department_id.display_name
            dict_obj['cost_center_name'] = line.cost_center_id.display_name
            dict_obj['partner_name'] = line.partner_id.display_name
            dict_obj['particulars'] = line.name
            dict_obj['debit'] = line.debit
            dict_obj['credit'] = line.credit
            report_data['lines'].append(dict_obj)

        docargs = {
            'data': report_data,
            'title': report_title,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('gbs_voucher.voucher_report', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)
