from odoo import api, models, fields
from odoo.tools.misc import formatLang


class GBSJournalItemsReport(models.AbstractModel):
    _name = 'report.account_journal_report.journal_items_report'

    @api.multi
    def render_html(self, docids, data=None):

        report_utility_pool = self.env['report.utility']
        # set report title
        report_title = 'Journal Item Report'
        report_data = {}
        report_data['lines'] = []

        sum_of_credit = 0
        sum_of_debit = 0
        aml_obj_list = self.env['account.move.line'].browse(docids)

        for line in aml_obj_list:
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
            dict_obj['date'] = report_utility_pool.get_date_from_string(line.date)
            dict_obj['journal'] = line.move_id.name

            sum_of_credit = sum_of_credit + line.credit
            sum_of_debit = sum_of_debit + line.debit

            report_data['lines'].append(dict_obj)

        report_data['sum_of_credit'] = sum_of_credit
        report_data['sum_of_debit'] = sum_of_debit
        if sum_of_credit == sum_of_debit:
            report_data['word_amount'] = self.env['res.currency'].amount_to_word(float(sum_of_credit))
        else:
            report_data['word_amount'] = ''



        docargs = {
            'data': report_data,
            'title': report_title,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('account_journal_report.journal_items_report', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)
