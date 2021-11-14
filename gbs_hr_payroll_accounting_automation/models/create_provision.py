from odoo import api, fields, models, _
from datetime import datetime
from collections import OrderedDict
import operator, math, locale
from odoo.exceptions import UserError


class CreateProvision(models.Model):
    _name = 'hr.payslip.run.create.provision'
    _description = 'Description'
    _rec_name = 'payslip_run_id'

    def _default_payslip_run(self):
        return self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))

    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        default=lambda self: self._default_payslip_run(),
        string='Payslip Run',
        required=True
    )

    def _default_journal_entry(self):
        run = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return run.journal_entry

    journal_entry = fields.Integer(default=lambda self: self._default_journal_entry())

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

    payable_account = fields.Many2one('account.account',
                                      required=True, readonly=True,
                                      default=lambda self: self._default_payable_account(),
                                      string='Payable GL')

    def _default_tds_payable_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.tds_payable_account

    tds_payable_account = fields.Many2one('account.account', readonly=True, required=True,
                                          default=lambda self: self._default_tds_payable_account(),
                                          string='TDS Payable GL')

    def _default_telephone_bill_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.telephone_bill_account

    telephone_bill_account = fields.Many2one('account.account', readonly=True, required=True,
                                             default=lambda self: self._default_telephone_bill_account(),
                                             string='Telephone Bill GL')

    def _default_employee_pf_contribution_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.employee_pf_contribution_account

    employee_pf_contribution_account = fields.Many2one('account.account', required=True, readonly=True,
                                                       default=lambda
                                                           self: self._default_employee_pf_contribution_account(),
                                                       string='Employee PF Contribution GL')

    def _default_company_pf_contribution_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.company_pf_contribution_account

    company_pf_contribution_account = fields.Many2one('account.account', required=True, readonly=True,
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
        res = super(CreateProvision, self).default_get(fields)
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        if payslip_run_obj.operating_unit_id.debit_account_ids:
            debit_account_lines = [(5, 0, 0)]
            for debit_account in payslip_run_obj.operating_unit_id.debit_account_ids:
                line = (0, 0, {
                    'department_id': debit_account.department_id.id,
                    'account_id': debit_account.account_id.id
                })
                debit_account_lines.append(line)
            res.update({'debit_account_ids': debit_account_lines})
        else:
            print('not debit accounts found')
        return res

    debit_account_ids = fields.One2many('temp.department.account.map', 'provision_id',
                                        string="""Debit GL's""")

    def _default_journal(self):
        account_journal = self.env['account.journal'].sudo().search([('code', '=', 'SPJNL')])
        return account_journal

    journal_id = fields.Many2one('account.journal', readonly=True, required=True,
                                 default=lambda self: self._default_journal(),
                                 string='Journal')
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
            if not slip.employee_id.cost_center_id:
                raise UserError(_('Cannot create journal entry because employee does not have cost center '
                                  'configured.'))
            if not slip.employee_id.department_id:
                raise UserError(_('Cannot create journal entry because employee does not have department '
                                  'configured.'))
            if not slip.employee_id.operating_unit_id:
                raise UserError(_('Cannot create journal entry because employee does not have operating unit '
                                  'configured.'))

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
        # cost_centers = self.env['account.cost.center'].sudo().search([])

        cost_center_list = []
        for key, value in record.items():
            # check which cost center available under this department
            for slip in top_sheet.slip_ids:
                if slip.employee_id.department_id.name == key:
                    if slip.employee_id.cost_center_id:
                        cost_center_list.append(slip.employee_id.cost_center_id)

                    # then add cost center of that employee

            cost_center_list = list(dict.fromkeys(cost_center_list))
            # print('department, cost centers', key, cost_center_list)
            # get cost center net values under department
            department_net[key] = {}

            # department_net[key]['net'] = 0
            for cost_center in cost_center_list:
                department_net[key][cost_center] = 0

            # sum = 0
            # for rule_key, rule_value in value['vals'].items():
            #     sum = sum + rule_value
            # department_net[key]['net'] = sum

        # (u'H2O2 (E & I)', {'net': 246232.0})

        for key, value in department_net.items():
            # a cost center and a department total net value

            # get_total_net_value_of_this_cost_center_department
            for cost_center in value:
                sum = 0
                for slip in top_sheet.slip_ids:
                    # print('cost center id 1 ', slip.employee_id.cost_center_id)
                    # print('cost center id 2 ', cost_center.id)
                    if slip.employee_id.department_id.name == key and slip.employee_id.cost_center_id.id == cost_center.id:

                        for line in slip.line_ids:
                            if line.appears_on_payslip and line.code == 'NET':
                                sum = sum + math.ceil(line.total)

                department_net[key][cost_center] = sum

        return department_net

    def get_top_sheet_total_net_value(self, top_sheet):
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

        # getting last column total value from top sheet
        last_value = total.get(total.keys()[-1])
        return last_value

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
            # check if journal entry created for this payslip run
            entry_exist = self.env['account.move'].sudo().search([('payslip_run_id', '=', self.payslip_run_id.id)])

            if entry_exist:
                raise UserError(_('Journal Entry already created for this payslip batch.'))
            payslip_list = self.get_payslip_list(self.payslip_run_id)
            department_net_values = self.get_department_net_values(self.payslip_run_id)
            top_sheet_total_net_value = self.get_top_sheet_total_net_value(self.payslip_run_id)

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

            journal_id = self.env['account.journal'].sudo().search([('code', '=', 'SPJNL')])
            # here
            if self.payslip_run_id.operating_unit_id:
                if self.payslip_run_id.operating_unit_id.debit_account_ids:
                    # operating unit has department wise debit account

                    datem = datetime.strptime(self.date, '%Y-%m-%d').strftime('%m')
                    month = datetime.strptime(self.date, '%Y-%m-%d').strftime("%B")
                    datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')
                    move_lines = []
                    sum_debit = 0
                    sum_credit = 0

                    for key, value in department_net_values.items():
                        for cost_center_value in value:
                            department = self.env['hr.department'].sudo().search([('name', '=', key)])
                            debit_account_obj = self.env['department.account.map'].sudo().search(
                                [('department_id', '=', department.id),
                                 ('operating_unit_id', '=', self.payslip_run_id.operating_unit_id.id)])
                            if debit_account_obj:
                                debit_vals = {
                                    'name': '0',
                                    'date': self.date,
                                    'journal_id': journal_id.id,
                                    'account_id': debit_account_obj.account_id.id,
                                    'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                    'department_id': department.id,
                                    'cost_center_id': cost_center_value.id,
                                    'debit': department_net_values[key][cost_center_value],
                                    'credit': 0,
                                    'company_id': self.operating_unit_id.company_id.id,
                                }
                            else:
                                debit_vals = {
                                    'name': '0',
                                    'date': self.date,
                                    'journal_id': journal_id.id,
                                    'account_id': self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                    'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                    'department_id': department.id,
                                    'cost_center_id': cost_center_value.id,
                                    'debit': department_net_values[key][cost_center_value],
                                    'credit': 0,
                                    'company_id': self.operating_unit_id.company_id.id,
                                }

                            sum_debit = sum_debit + department_net_values[key][cost_center_value]

                            move_lines.append((0, 0, debit_vals))
                    print('sum debit', sum_debit)
                    tds_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.tds_payable_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': total_tax_deducted_source,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, tds_credit_vals))
                    sum_credit = sum_credit + total_tax_deducted_source
                    pf_com_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.company_pf_contribution_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': company_pf_contribution,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, pf_com_credit_vals))
                    sum_credit = sum_credit + company_pf_contribution
                    pf_emp_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': employee_pf_contribution,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, pf_emp_credit_vals))
                    sum_credit = sum_credit + employee_pf_contribution

                    telephone_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': telephone_mobile_bill,
                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, telephone_credit_vals))
                    sum_credit = sum_credit + telephone_mobile_bill

                    main_credit_vals = {
                        'name': '0',
                        'date': self.date,
                        'journal_id': journal_id.id,
                        'account_id': self.payslip_run_id.operating_unit_id.payable_account.id,
                        'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                        'department_id': department.id,
                        'debit': 0,
                        'credit': sum_debit - (
                                total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),

                        'company_id': self.operating_unit_id.company_id.id,
                    }
                    move_lines.append((0, 0, main_credit_vals))
                    sum_credit = sum_credit + sum_debit - (
                            total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill)

                    print('sum credit', sum_credit)

                    name_seq = self.env['ir.sequence'].next_by_code('account.move.seq')

                    difference = 0
                    if sum_credit > top_sheet_total_net_value:
                        difference = sum_credit - top_sheet_total_net_value
                    elif sum_credit < top_sheet_total_net_value:
                        difference = top_sheet_total_net_value - sum_credit
                    else:
                        difference = 0

                    if difference == 0:
                        # return wizard to confirm
                        vals = {
                            'name': name_seq,
                            'journal_id': journal_id.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'date': self.date,
                            'company_id': self.company_id.id,
                            'state': 'draft',
                            'line_ids': move_lines,
                            'payslip_run_id': self.payslip_run_id.id,
                            'narration': 'Provision above amount against Salary month of ' + month + '-' + datey,
                            'ref': '',
                            # Provision above amount against Salary month of July - 2021
                        }

                        move = self.env['account.move'].create(vals)

                    else:
                        # return wizard to confirm
                        vals = {
                            'name': name_seq,
                            'journal_id': journal_id.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'date': self.date,
                            'company_id': self.company_id.id,
                            'state': 'draft',
                            'line_ids': move_lines,
                            'payslip_run_id': self.payslip_run_id.id,
                            'narration': 'Provision above amount against Salary month of ' + month + '-' + datey,
                            'ref': 'Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. ' % difference,
                            # Provision above amount against Salary month of July - 2021
                        }

                        message_id = self.env['confirmation.wizard'].create({'message': _(
                            "Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. Are you sure to create journal entry?" % difference)
                        })
                        return {
                            'name': _('Confirmation'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'confirmation.wizard',
                            'context': vals,
                            'res_id': message_id.id,
                            'target': 'new'
                        }


                else:
                    if self.payslip_run_id.operating_unit_id.default_debit_account:
                        # operating unit has default debit account

                        datem = datetime.strptime(self.date, '%Y-%m-%d').strftime('%m')
                        month = datetime.strptime(self.date, '%Y-%m-%d').strftime("%B")
                        datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')
                        move_lines = []
                        sum_debit = 0
                        sum_credit = 0

                        for key, value in department_net_values.items():
                            for cost_center_value in value:
                                department = self.env['hr.department'].sudo().search([('name', '=', key)])
                                debit_vals = {
                                    'name': '0',
                                    'date': self.date,
                                    'journal_id': journal_id.id,
                                    'account_id': self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                    'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                    'department_id': department.id,
                                    'cost_center_id': cost_center_value.id,
                                    'debit': department_net_values[key][cost_center_value],
                                    'credit': 0,
                                    'company_id': self.operating_unit_id.company_id.id,
                                }

                                sum_debit = sum_debit + department_net_values[key][cost_center_value]

                                move_lines.append((0, 0, debit_vals))
                        print('sum debit', sum_debit)

                        tds_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.tds_payable_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': total_tax_deducted_source,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, tds_credit_vals))
                        sum_credit = sum_credit + total_tax_deducted_source
                        pf_com_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.company_pf_contribution_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': company_pf_contribution,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, pf_com_credit_vals))
                        sum_credit = sum_credit + company_pf_contribution
                        pf_emp_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': employee_pf_contribution,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, pf_emp_credit_vals))
                        sum_credit = sum_credit + employee_pf_contribution
                        telephone_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': telephone_mobile_bill,
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, telephone_credit_vals))
                        sum_credit = sum_credit + telephone_mobile_bill
                        main_credit_vals = {
                            'name': '0',
                            'date': self.date,
                            'journal_id': journal_id.id,
                            'account_id': self.payslip_run_id.operating_unit_id.payable_account.id,
                            'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                            'department_id': department.id,
                            'debit': 0,
                            'credit': sum_debit - (
                                    total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),
                            'company_id': self.operating_unit_id.company_id.id,
                        }
                        move_lines.append((0, 0, main_credit_vals))
                        sum_credit = sum_credit + sum_debit - (
                                total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill)

                        print('sum credit', sum_credit)
                        name_seq = self.env['ir.sequence'].next_by_code('account.move.seq')

                        difference = 0
                        if sum_credit > top_sheet_total_net_value:
                            difference = sum_credit - top_sheet_total_net_value
                        elif sum_credit < top_sheet_total_net_value:
                            difference = top_sheet_total_net_value - sum_credit
                        else:
                            difference = 0

                        if difference == 0:
                            # return wizard to confirm
                            vals = {
                                'name': name_seq,
                                'journal_id': journal_id.id,
                                'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                'date': self.date,
                                'company_id': self.company_id.id,
                                'state': 'draft',
                                'line_ids': move_lines,
                                'payslip_run_id': self.payslip_run_id.id,
                                'narration': 'Provision above amount against Salary month of ' + month + '-' + datey,
                                'ref': '',
                                # Provision above amount against Salary month of July - 2021
                            }

                            move = self.env['account.move'].create(vals)

                        else:
                            # return wizard to confirm
                            vals = {
                                'name': name_seq,
                                'journal_id': journal_id.id,
                                'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                                'date': self.date,
                                'company_id': self.company_id.id,
                                'state': 'draft',
                                'line_ids': move_lines,
                                'payslip_run_id': self.payslip_run_id.id,
                                'narration': 'Provision above amount against Salary month of ' + month + '-' + datey,
                                'ref': 'Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. ' % difference,
                                # Provision above amount against Salary month of July - 2021
                            }

                            message_id = self.env['confirmation.wizard'].create({'message': _(
                                "Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. Are you sure to create journal entry?" % difference)
                            })
                            return {
                                'name': _('Confirmation'),
                                'type': 'ir.actions.act_window',
                                'view_mode': 'form',
                                'res_model': 'confirmation.wizard',
                                'context': vals,
                                'res_id': message_id.id,
                                'target': 'new'
                            }

    def load_values(self):
        if self.payslip_run_id:
            debit_account_lines = []
            # if self.payslip_run_id.operating_unit_id.debit_account_ids:
            #     for debit_account in self.payslip_run_id.operating_unit_id.debit_account_ids:
            #         line = (0, 0, {
            #             'department_id': debit_account.department_id.id,
            #             'account_id': debit_account.account_id.id,
            #             'operating_unit_id': debit_account.operating_unit_id.id
            #         })
            #         debit_account_lines.append(line)
            provision_obj = self.env['hr.payslip.run.create.provision'].browse(self.id)
            provision_obj.write({'debit_account_ids': self.payslip_run_id.operating_unit_id.debit_account_ids})
            # self.debit_account_ids = debit_account_lines
