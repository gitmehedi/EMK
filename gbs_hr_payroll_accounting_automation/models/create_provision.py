from odoo import api, fields, models, _
from datetime import datetime
from collections import OrderedDict
import operator, math, locale
from odoo.exceptions import UserError


class CreateProvision(models.TransientModel):
    _name = 'hr.payslip.run.create.provision'
    _description = 'Create Provision'
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
        cost_center_list = []
        for key, value in record.items():
            # check which cost center available under this department
            for slip in top_sheet.slip_ids:
                department_id = slip.employee_id.department_id.id
                if slip.employee_id.department_id.name == key:
                    if slip.employee_id.cost_center_id:
                        cost_center_list.append(slip.employee_id.cost_center_id)

                    # then add cost center of that employee
            cost_center_list = list(dict.fromkeys(cost_center_list))

            department_net[key] = {}

            for cost_center in cost_center_list:
                department_net[key][cost_center] = 0

        for key, value in department_net.items():
            # a cost center and a department total net value
            # get_total_net_value_of_this_cost_center_department
            for cost_center in value:
                sum = 0
                for slip in top_sheet.slip_ids:
                    if slip.employee_id.department_id.name == key and slip.employee_id.cost_center_id.id == cost_center.id:

                        for line in slip.line_ids:
                            if line.appears_on_payslip and line.code == 'NET':
                                sum = sum + math.ceil(line.total)

                department_net[key][cost_center] = sum

        return department_net

    def get_departments(self, top_sheet):
        departments = []
        for slip in top_sheet.slip_ids:
            departments.append(slip.employee_id.department_id)
        departments = list(dict.fromkeys(departments))
        return departments

    def get_cost_centers(self, top_sheet):
        cost_centers = []
        for slip in top_sheet.slip_ids:
            if slip.employee_id.cost_center_id:
                cost_centers.append(slip.employee_id.cost_center_id)
            else:
                raise UserError(_('Cannot create journal entry because employee does not have cost center '
                                  'configured.'))
        cost_centers = list(dict.fromkeys(cost_centers))
        return cost_centers

    def get_department_id(self, payslip_departments, key):
        for department in payslip_departments:
            if department.name == key:
                return department

    def populate_record_dict(self, record, top_sheet, rule_list):
        for slip in top_sheet.slip_ids:
            for line in slip.line_ids:
                if (line.sequence, line.name) not in rule_list and line.appears_on_payslip:
                    rule_list.append((line.sequence, line.name))

        rule_list = sorted(rule_list, key=lambda k: k[0])
        for rec in top_sheet.slip_ids:
            rules = OrderedDict()
            for rule in rule_list:
                rules[rule[1]] = 0
            record[rec.employee_id.department_id.name] = {}
            record[rec.employee_id.department_id.name]['count'] = 0
            record[rec.employee_id.department_id.name]['vals'] = rules

    def get_sum_value(self, top_sheet, record, code, code_value):
        for slip in top_sheet.slip_ids:
            rec = record[slip.employee_id.department_id.name]
            rec['count'] = rec['count'] + 1
            for line in slip.line_ids:
                if line.code == code:
                    rec['vals'][line.name] = rec['vals'][line.name] + math.ceil(line.total)

        department_net = OrderedDict()

        for key, value in record.items():
            department_net[key] = {}
            department_net[key][code_value] = 0
            sum = 0
            for rule_key, rule_value in value['vals'].items():
                sum = sum + rule_value
            department_net[key][code_value] = sum

        sum_value = 0
        for key, value in department_net.items():
            sum_value = sum_value + value[code_value]

        return sum_value

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
        record = OrderedDict()
        self.populate_record_dict(record, top_sheet, rule_list)
        sum_tds = self.get_sum_value(top_sheet, record, 'TDS', 'tds')

        return sum_tds

    def get_employee_pf_contribution(self, top_sheet):
        rule_list = []
        record = OrderedDict()
        self.populate_record_dict(record, top_sheet, rule_list)
        sum_emp_pf_cont = self.get_sum_value(top_sheet, record, 'EPMF', 'empf')

        return sum_emp_pf_cont

    def get_telephone_mobile_bill(self, top_sheet):
        rule_list = []
        record = OrderedDict()
        self.populate_record_dict(record, top_sheet, rule_list)
        sum_telephone_bill = self.get_sum_value(top_sheet, record, 'MOBILE', 'mobile')

        return sum_telephone_bill

    def get_a_cost_center_telephone_bill(self, cost_center, top_sheet):
        employee_list = []
        sum = 0
        for rec in top_sheet.slip_ids:
            if rec.employee_id.cost_center_id.id == cost_center.id:
                employee_list.append(rec.employee_id)
                for line in rec.line_ids:
                    if line.code == 'MOBILE':
                        sum = sum + math.ceil(line.total)
        return sum

    def get_cost_center_wise_telephone_bill(self, payslip_cost_centers, top_sheet):
        cost_center_telephone_dict = OrderedDict()
        for cost_center in payslip_cost_centers:
            cost_center_telephone_dict[cost_center.id] = {}
            cost_center_telephone_dict[cost_center.id]['vals'] = 0

        for cost_center in payslip_cost_centers:
            cost_center_telephone_bill = self.get_a_cost_center_telephone_bill(cost_center, top_sheet)
            cost_center_telephone_dict[cost_center.id]['vals'] = cost_center_telephone_bill

        return cost_center_telephone_dict

    def get_move_line_vals(self, name, date, journal_id, account_id, operating_unit_id, department_id, cost_center_id,
                           debit, credit,
                           company_id):
        return {
            'name': name,
            'date': date,
            'journal_id': journal_id,
            'account_id': account_id,
            'operating_unit_id': operating_unit_id,
            'department_id': department_id,
            'cost_center_id': cost_center_id,
            'debit': debit,
            'credit': credit,
            'company_id': company_id,
        }

    def create_provision(self):
        if self.payslip_run_id:
            # check if journal entry created for this payslip run
            if self.payslip_run_id.account_move_id:
                raise UserError(_('Journal Entry already created for this payslip batch.'))

            department_net_values = self.get_department_net_values(self.payslip_run_id)
            payslip_departments = self.get_departments(self.payslip_run_id)
            payslip_cost_centers = self.get_cost_centers(self.payslip_run_id)
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

            cost_center_wise_telephone_bill = self.get_cost_center_wise_telephone_bill(payslip_cost_centers,
                                                                                       self.payslip_run_id)

            journal_id = self.env['account.journal'].sudo().search([('code', '=', 'SPJNL')])

            if self.payslip_run_id.operating_unit_id:
                month = datetime.strptime(self.date, '%Y-%m-%d').strftime("%B")
                datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')
                move_lines = []
                sum_debit = 0
                sum_credit = 0
                tds_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                          self.payslip_run_id.operating_unit_id.tds_payable_account.id,
                                                          self.payslip_run_id.operating_unit_id.id, False, False, 0,
                                                          total_tax_deducted_source,
                                                          self.operating_unit_id.company_id.id)

                sum_credit = sum_credit + total_tax_deducted_source

                pf_com_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                             self.payslip_run_id.operating_unit_id.company_pf_contribution_account.id,
                                                             self.payslip_run_id.operating_unit_id.id, 0, False, False,
                                                             company_pf_contribution,
                                                             self.operating_unit_id.company_id.id)

                sum_credit = sum_credit + company_pf_contribution

                pf_emp_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                             self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                                                             self.payslip_run_id.operating_unit_id.id, 0, False, False,
                                                             employee_pf_contribution,
                                                             self.operating_unit_id.company_id.id)

                sum_credit = sum_credit + employee_pf_contribution

                if self.payslip_run_id.operating_unit_id.debit_account_ids:
                    for key, value in department_net_values.items():
                        for cost_center_value in value:
                            department = self.get_department_id(payslip_departments, key)
                            debit_account_obj = self.env['department.account.map'].sudo().search(
                                [('department_id', '=', department.id),
                                 ('operating_unit_id', '=', self.payslip_run_id.operating_unit_id.id)])
                            if debit_account_obj:
                                debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                     debit_account_obj.account_id.id,
                                                                     self.payslip_run_id.operating_unit_id.id,
                                                                     department.id, cost_center_value.id,
                                                                     department_net_values[key][cost_center_value], 0,
                                                                     self.operating_unit_id.company_id.id)

                            else:
                                debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                     self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                     self.payslip_run_id.operating_unit_id.id,
                                                                     department.id, cost_center_value.id,
                                                                     department_net_values[key][cost_center_value], 0,
                                                                     self.operating_unit_id.company_id.id)

                            sum_debit = sum_debit + department_net_values[key][cost_center_value]

                            if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                move_lines.append((0, 0, debit_vals))

                    total_telephone_credit_vals = 0
                    for key, value in cost_center_wise_telephone_bill.items():
                        if value['vals'] < 0:
                            value['vals'] = value['vals'] * (-1)
                        if not value['vals'] == 0:
                            telephone_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                            self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                                                                            self.payslip_run_id.operating_unit_id.id,
                                                                            False,
                                                                            key,
                                                                            0,
                                                                            value['vals'],
                                                                            self.operating_unit_id.company_id.id)

                            move_lines.append((0, 0, telephone_credit_vals))
                            total_telephone_credit_vals = total_telephone_credit_vals + value['vals']
                    sum_credit = sum_credit + telephone_mobile_bill

                    main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                               self.payslip_run_id.operating_unit_id.payable_account.id,
                                                               self.payslip_run_id.operating_unit_id.id, False, False,
                                                               0, sum_debit - (
                                                                       total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),
                                                               self.operating_unit_id.company_id.id)

                    move_lines.append((0, 0, tds_credit_vals))
                    move_lines.append((0, 0, pf_com_credit_vals))
                    move_lines.append((0, 0, pf_emp_credit_vals))
                    move_lines.append((0, 0, main_credit_vals))
                    sum_credit = sum_credit + sum_debit - (
                            total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill)
                else:
                    if self.payslip_run_id.operating_unit_id.default_debit_account:
                        for key, value in department_net_values.items():
                            for cost_center_value in value:
                                department = self.get_department_id(payslip_departments, key)

                                debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                     self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                     self.payslip_run_id.operating_unit_id.id,
                                                                     department.id, cost_center_value.id,
                                                                     department_net_values[key][
                                                                         cost_center_value], 0,
                                                                     self.operating_unit_id.company_id.id)

                                sum_debit = sum_debit + department_net_values[key][cost_center_value]

                                if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                    move_lines.append((0, 0, debit_vals))

                        total_telephone_credit_vals = 0
                        for key, value in cost_center_wise_telephone_bill.items():
                            if value['vals'] < 0:
                                value['vals'] = value['vals'] * (-1)
                            if not value['vals'] == 0:
                                telephone_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                                self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                                                                                self.payslip_run_id.operating_unit_id.id,
                                                                                False,
                                                                                key,
                                                                                0,
                                                                                value['vals'],
                                                                                self.operating_unit_id.company_id.id)

                                move_lines.append((0, 0, telephone_credit_vals))
                                total_telephone_credit_vals = total_telephone_credit_vals + value['vals']
                        sum_credit = sum_credit + telephone_mobile_bill

                        main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                   self.payslip_run_id.operating_unit_id.payable_account.id,
                                                                   self.payslip_run_id.operating_unit_id.id, False,
                                                                   False,
                                                                   0, sum_debit - (
                                                                               total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),
                                                                   self.operating_unit_id.company_id.id)

                        move_lines.append((0, 0, tds_credit_vals))
                        move_lines.append((0, 0, pf_com_credit_vals))
                        move_lines.append((0, 0, pf_emp_credit_vals))
                        move_lines.append((0, 0, main_credit_vals))
                        sum_credit = sum_credit + sum_debit - (
                                    total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill)

                name_seq = self.env['ir.sequence'].next_by_code('account.move.seq')
                difference = 0
                if sum_credit == sum_debit:
                    if sum_credit > top_sheet_total_net_value:
                        difference = sum_credit - top_sheet_total_net_value
                    elif sum_credit < top_sheet_total_net_value:
                        difference = top_sheet_total_net_value - sum_credit
                    else:
                        difference = 0
                else:
                    raise UserError(_('Total debit value and total credit value mismatched.'))
                if difference == 0:
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
                        'ref': 'Total net value : ' + str(top_sheet_total_net_value)
                    }
                    move = self.env['account.move'].create(vals)
                    if move:
                        self.payslip_run_id.write({'account_move_id': move.id})
                        message_id = self.env['success.wizard'].create({'message': _(
                            "Journal Entry Created Successfully!")
                        })
                        return {
                            'name': _('Success'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'success.wizard',
                            'context': vals,
                            'res_id': message_id.id,
                            'target': 'new'
                        }
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
                        'ref': 'Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. ' % difference

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
            raise UserError(_('Payslip Batch not found!'))
