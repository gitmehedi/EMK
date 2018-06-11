import operator, math, locale
from collections import OrderedDict

from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_payroll_top_sheet.report_top_sheet'

    # def getKey(item):
    #     return item[1]

    @api.model
    def render_html(self, docids, data=None):
        top_sheet = self.env['hr.payslip.run'].browse(docids[0])

        data['name'] = top_sheet.name

        rule_list = []
        for slip in top_sheet.slip_ids:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])

        header = OrderedDict()
        header[0] = 'Department'
        header[1] = 'Employee'
        for rec in rule_list:
            header[len(header)] = rec[1]

        record = OrderedDict()
        for rec in top_sheet.slip_ids:
            rules = OrderedDict()
            for rule in rule_list:
                rules[rule[1]] = 0
            record[rec.employee_id.department_id.name] = {}
            record[rec.employee_id.department_id.name]['count'] = 0
            record[rec.employee_id.department_id.name]['vals'] = rules

        total = OrderedDict()
        for rule in rule_list:
            total[rule[1]] = 0


        bnet = 0
        net = 0

        for slip in top_sheet.slip_ids:
            rec = record[slip.employee_id.department_id.name]
            rec['count'] = rec['count'] + 1
            for line in slip.line_ids:
                if line.appears_on_payslip:
                    rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)
                    total[line.name] = total[line.name] + math.ceil(line.total)
                if line.code == 'BNET' and slip.employee_id.bank_account_id.bank_id:
                    bnet = bnet + math.ceil(line.total)
                if line.code == 'NET':
                    net = net + math.ceil(line.total)

        total_cash = net-bnet
        amt_to_word_bnet = self.env['res.currency'].amount_to_word(float(bnet))
        amt_to_word_net = self.env['res.currency'].amount_to_word(float(net))
        amt_to_word_cash = self.env['res.currency'].amount_to_word(float(total_cash))

        docargs = {

            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'header': header,
            'data': data,
            'record': record,
            'total': total,
            'rules': rule_list,
            'bnet': formatLang(self.env,(bnet)),
            'net': formatLang(self.env,(net)),
            'total_cash': formatLang(self.env,(net-bnet)),
            'amt_to_word_bnet': amt_to_word_bnet,
            'amt_to_word_net': amt_to_word_net,
            'amt_to_word_cash': amt_to_word_cash,

        }

        return self.env['report'].render('gbs_hr_payroll_top_sheet.report_top_sheet', docargs)
