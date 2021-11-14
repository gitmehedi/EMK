from odoo import models, fields, api
from datetime import datetime
from collections import OrderedDict
import operator, math, locale
from odoo import api, exceptions, fields, models


class GLAutomapperWizard(models.TransientModel):
    _name = 'hr.payslip.run.gl.automapper'

    def _default_payslip_run(self):
        return self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))

    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        default=lambda self: self._default_payslip_run(),
        string='Payslip Run',
        required=True
    )

    def _default_operating_unit(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))

        return payslip_run_obj.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit', default=lambda self: self._default_operating_unit(),
                                        string='Operating Unit')

    def _default_payable_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.payable_account

    payable_account = fields.Many2one('account.account', readonly=True,
                                      default=lambda self: self._default_payable_account(),
                                      string='Payable GL')

    def _default_tds_payable_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.tds_payable_account

    tds_payable_account = fields.Many2one('account.account', readonly=True,
                                          default=lambda self: self._default_tds_payable_account(),
                                          string='TDS Payable GL')

    def _default_telephone_bill_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.telephone_bill_account

    telephone_bill_account = fields.Many2one('account.account', readonly=True,
                                             default=lambda self: self._default_telephone_bill_account(),
                                             string='Telephone Bill GL')

    def _default_employee_pf_contribution_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.employee_pf_contribution_account

    employee_pf_contribution_account = fields.Many2one('account.account', readonly=True,
                                                       default=lambda
                                                           self: self._default_employee_pf_contribution_account(),
                                                       string='Employee PF Contribution GL')

    def _default_company_pf_contribution_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.company_pf_contribution_account

    company_pf_contribution_account = fields.Many2one('account.account', readonly=True,
                                                      default=lambda
                                                          self: self._default_company_pf_contribution_account(),
                                                      string='Company PF Contribution GL')

    def _default_debit_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.default_debit_account

    default_debit_account = fields.Many2one('account.account', readonly=True,
                                            default=lambda self: self._default_debit_account(),
                                            string='Default Debit GL')

    @api.model
    def default_get(self, fields):
        res = super(GLAutomapperWizard, self).default_get(fields)
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        if payslip_run_obj.operating_unit_id.debit_account_ids:
            debit_account_lines = [(5, 0, 0)]
            for debit_account in payslip_run_obj.operating_unit_id.debit_account_ids:
                line = (0, 0, {
                    'department_id': debit_account.department_id.id,
                    'account_id': debit_account.account_id.id,
                    'operating_unit_id': debit_account.operating_unit_id.id
                })
                debit_account_lines.append(line)
            # res.update({'debit_account_ids': debit_account_lines})
        else:
            print('not debit accounts found')
        return res

    journal_id = fields.Many2one('account.journal', required=True, string='Journal')
    date = fields.Date(required=True, default=fields.Date.context_today)

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )

    def get_payslip_list(self, payslip_run_id):
        self.env.cr.execute("""
                            select id from hr_payslip where payslip_run_id = %s
                        """ % (payslip_run_id.id))
        payslip_list = []
        for id in self.env.cr.fetchall():
            payslip_list.append(self.env['hr.payslip'].browse(id))
        return payslip_list

    def get_department_net_values(self, top_sheet):

        rule_list = []
        for slip in top_sheet.slip_ids:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])

        record = OrderedDict()
        for rec in top_sheet.slip_ids:
            rules = OrderedDict()
            for rule in rule_list:
                rules[rule[1]] = 0
            record[rec.employee_id.department_id.name] = {}
            record[rec.employee_id.department_id.name]['count'] = 0
            record[rec.employee_id.department_id.name]['vals'] = rules

        for slip in top_sheet.slip_ids:
            rec = record[slip.employee_id.department_id.name]
            rec['count'] = rec['count'] + 1
            for line in slip.line_ids:
                if line.appears_on_payslip and line.code == 'NET':
                    rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)

        department_net = OrderedDict()

        for key, value in record.items():
            department_net[key] = {}
            department_net[key]['net'] = 0
            sum = 0
            for rule_key, rule_value in value['vals'].items():
                sum = sum + rule_value
            department_net[key]['net'] = sum

        return department_net

    def get_total_tds_value(self, top_sheet):

        rule_list = []
        for slip in top_sheet.slip_ids:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])

        record = OrderedDict()
        for rec in top_sheet.slip_ids:
            rules = OrderedDict()
            for rule in rule_list:
                rules[rule[1]] = 0
            record[rec.employee_id.department_id.name] = {}
            record[rec.employee_id.department_id.name]['count'] = 0
            record[rec.employee_id.department_id.name]['vals'] = rules

        for slip in top_sheet.slip_ids:
            rec = record[slip.employee_id.department_id.name]
            rec['count'] = rec['count'] + 1
            for line in slip.line_ids:
                if line.code == 'TDS':
                    rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)

        department_net = OrderedDict()

        for key, value in record.items():
            department_net[key] = {}
            department_net[key]['tds'] = 0
            sum = 0
            for rule_key, rule_value in value['vals'].items():
                sum = sum + rule_value
            department_net[key]['tds'] = sum

        sum_tds = 0
        for key, value in department_net.items():
            sum_tds = sum_tds + value['tds']

        return sum_tds

    def get_employee_pf_contribution(self, top_sheet):
        rule_list = []
        for slip in top_sheet.slip_ids:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])

        record = OrderedDict()
        for rec in top_sheet.slip_ids:
            rules = OrderedDict()
            for rule in rule_list:
                rules[rule[1]] = 0
            record[rec.employee_id.department_id.name] = {}
            record[rec.employee_id.department_id.name]['count'] = 0
            record[rec.employee_id.department_id.name]['vals'] = rules

        for slip in top_sheet.slip_ids:
            rec = record[slip.employee_id.department_id.name]
            rec['count'] = rec['count'] + 1
            for line in slip.line_ids:
                if line.code == 'EPMF':
                    rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)

        department_net = OrderedDict()

        for key, value in record.items():
            department_net[key] = {}
            department_net[key]['empf'] = 0
            sum = 0
            for rule_key, rule_value in value['vals'].items():
                sum = sum + rule_value
            department_net[key]['empf'] = sum

        sum_tds = 0
        for key, value in department_net.items():
            sum_tds = sum_tds + value['empf']

        return sum_tds

    def get_telephone_mobile_bill(self, top_sheet):
        rule_list = []
        for slip in top_sheet.slip_ids:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])

        record = OrderedDict()
        for rec in top_sheet.slip_ids:
            rules = OrderedDict()
            for rule in rule_list:
                rules[rule[1]] = 0
            record[rec.employee_id.department_id.name] = {}
            record[rec.employee_id.department_id.name]['count'] = 0
            record[rec.employee_id.department_id.name]['vals'] = rules

        for slip in top_sheet.slip_ids:
            rec = record[slip.employee_id.department_id.name]
            rec['count'] = rec['count'] + 1
            for line in slip.line_ids:
                if line.code == 'MOBILE':
                    rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)

        department_net = OrderedDict()

        for key, value in record.items():
            department_net[key] = {}
            department_net[key]['mobile'] = 0
            sum = 0
            for rule_key, rule_value in value['vals'].items():
                sum = sum + rule_value
            department_net[key]['mobile'] = sum

        sum_tds = 0
        for key, value in department_net.items():
            sum_tds = sum_tds + value['mobile']

        return sum_tds

    def create_provision(self):

        if self.payslip_run_id:
            payslip_list = self.get_payslip_list(self.payslip_run_id)
            department_net_values = self.get_department_net_values(self.payslip_run_id)
            total_tax_deducted_source = self.get_total_tds_value(self.payslip_run_id)
            if total_tax_deducted_source < 0:
                total_tax_deducted_source = total_tax_deducted_source * (-1)

            employee_pf_contribution = self.get_employee_pf_contribution(self.payslip_run_id)
            if employee_pf_contribution < 0:
                employee_pf_contribution = employee_pf_contribution * (-1)

            company_pf_contribution = employee_pf_contribution
            if company_pf_contribution < 0:
                company_pf_contribution = company_pf_contribution * (-1)
            telephone_mobile_bill = self.get_telephone_mobile_bill(self.payslip_run_id)
            if telephone_mobile_bill < 0:
                telephone_mobile_bill = telephone_mobile_bill * (-1)

            if self.payslip_run_id.operating_unit_id:
                if self.payslip_run_id.operating_unit_id.debit_account_ids:
                    # operating unit has department wise debit account
                    print('debit accounts')

                    datem = datetime.strptime(self.date, '%Y-%m-%d').strftime('%m')
                    datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')
                    move_lines = []
                    sum_credit = 0
                    # debit values
                    for key, value in department_net_values.items():
                        department = self.env['hr.department'].sudo().search([('name', '=', key)])
                        # search for account_id by department_id
                        debit_account_obj = self.payslip_run_id.operating_unit_id.debit_account_ids.sudo().search(
                            [('department_id', '=', department.id)])
                        print('debit account', debit_account_obj)
                        if debit_account_obj:
                            debit_vals = {
                                'name': '0',
                                'date': self.date,
                                'journal_id': self.journal_id.id,
                                'account_id': debit_account_obj.account_id.id,
                                'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                'department_id': department.id,
                                'debit': value['net'],
                                'credit': 0,
                                'company_id': self.operating_unit_id.company_id.id,
                            }
                        else:
                            debit_vals = {
                                'name': '0',
                                'date': self.date,
                                'journal_id': self.journal_id.id,
                                'account_id': self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                'department_id': department.id,
                                'debit': value['net'],
                                'credit': 0,
                                'company_id': self.operating_unit_id.company_id.id,
                            }

                        sum_credit = sum_credit + value['net']
                        move_lines.append((0, 0, debit_vals))

                    tds_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.tds_payable_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': total_tax_deducted_source,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, tds_credit_vals))

                    pf_com_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.company_pf_contribution_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': company_pf_contribution,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, pf_com_credit_vals))

                    pf_emp_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': employee_pf_contribution,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, pf_emp_credit_vals))

                    telephone_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': telephone_mobile_bill,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, telephone_credit_vals))

                    main_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.payable_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': sum_credit - (
                                total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, main_credit_vals))

                    vals = {
                        'name': 'Test Journal For provision 10 Nov',
                        'journal_id': self.journal_id.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'date': self.date,
                        'company_id': self.company_id.id,
                        'state': 'draft',
                        'line_ids': move_lines,
                        'payslip_run_id': self.payslip_run_id.id

                    }

                    move = self.env['account.move'].create(vals)
                else:
                    if self.payslip_run_id.operating_unit_id.default_debit_account:
                        # operating unit has default debit account

                        datem = datetime.strptime(self.date, '%Y-%m-%d').strftime('%m')
                        datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')
                        move_lines = []
                        sum_credit = 0
                        # debit values
                        for key, value in department_net_values.items():
                            department = self.env['hr.department'].sudo().search([('name', '=', key)])
                            debit_vals = {
                                'name': '0',
                                'date': self.date,
                                'journal_id': self.journal_id.id,
                                'account_id': self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                'department_id': department.id,
                                'debit': value['net'],
                                'credit': 0,
                                'company_id': self.operating_unit_id.company_id.id,
                            }

                            sum_credit = sum_credit + value['net']
                            move_lines.append((0, 0, debit_vals))

                        tds_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': self.journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.tds_payable_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': total_tax_deducted_source,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, tds_credit_vals))

                        pf_com_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': self.journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.company_pf_contribution_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': company_pf_contribution,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, pf_com_credit_vals))

                        pf_emp_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': self.journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': employee_pf_contribution,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, pf_emp_credit_vals))

                        telephone_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': self.journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': telephone_mobile_bill,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, telephone_credit_vals))

                        main_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': self.journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.payable_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': sum_credit - (
                                    total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, main_credit_vals))

                        vals = {
                            'name': 'Test Journal For provision 10 Nov',
                            'journal_id': self.journal_id.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'date': self.date,
                            'company_id': self.company_id.id,
                            'state': 'draft',
                            'line_ids': move_lines,
                            'payslip_run_id': self.payslip_run_id.id

                        }
                        #  'line_ids': move_lines
                        move = self.env['account.move'].create(vals)
