import operator, math, locale
from collections import OrderedDict

from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class PayrollReportPivotal(models.AbstractModel):
    _name = 'report.gbs_hr_payroll_top_sheet.report_top_sheet'

    def formatDigits(self, digits):
        return formatLang(self.env, digits)

    @api.model
    def render_html(self, docids, data=None):
        top_sheet = self.env['hr.payslip.run'].browse(data.get('active_id'))

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

        inword = {
            'total_cash': formatLang(self.env, (net - bnet)),
            'bnet_word': self.env['res.currency'].amount_to_word(float(bnet)),
            'net_word': self.env['res.currency'].amount_to_word(float(net)),
            'cash_word': self.env['res.currency'].amount_to_word(float(net - bnet)),
            'bnet': formatLang(self.env, bnet),
            'net': formatLang(self.env, net),
            'cash': formatLang(self.env, float(net - bnet)),
        }

        bank_list = []
        payroll_advice = self.env['hr.payroll.advice'].search([('name','=', top_sheet.name)])
        for i in payroll_advice:
            vals = {}
            vals['bank_name'] = i.bank_id.name
            vals['bank_acc_id'] = i.bank_acc_id.acc_number
            bysal = 0.0
            for line in i.line_ids:
                bysal = bysal+line.bysal
            vals['bysal'] =  formatLang(self.env,(math.ceil(bysal)))
            bank_list.append(vals)


        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'formatLang': self.formatDigits,
            'header': header,
            'data': data,
            'record': record,
            'total': total,
            'rules': rule_list,
            'bank_list': bank_list,
            'inword': inword
        }

        return self.env['report'].render('gbs_hr_payroll_top_sheet.report_top_sheet', docargs)
