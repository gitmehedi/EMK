from odoo import api, fields, models, _
from datetime import datetime, date, time, timedelta
from collections import OrderedDict
import operator, math, locale
from odoo.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT


class CreateProvision(models.TransientModel):
    _name = 'hr.payslip.run.create.provision'
    _description = 'Create Provision'
    _rec_name = 'payslip_run_id'

    def _default_payslip_run(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj

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
        return payslip_run_obj.operating_unit_id.payable_account if payslip_run_obj.operating_unit_id.payable_account else False

    payable_account = fields.Many2one('account.account',
                                      readonly=True,
                                      default=lambda self: self._default_payable_account(),
                                      string='Payable GL')

    def _default_ot_payable_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.payable_account_ot if payslip_run_obj.operating_unit_id.payable_account_ot else False

    payable_account_ot = fields.Many2one('account.account',
                                      readonly=True,
                                      default=lambda self: self._default_ot_payable_account(),
                                      string='OT Payable GL')

    def _default_tds_payable_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.tds_payable_account if payslip_run_obj.operating_unit_id.tds_payable_account else False

    tds_payable_account = fields.Many2one('account.account', readonly=True,
                                          default=lambda self: self._default_tds_payable_account(),
                                          string='TDS Payable GL')

    def _default_telephone_bill_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.telephone_bill_account if payslip_run_obj.operating_unit_id.telephone_bill_account else False

    telephone_bill_account = fields.Many2one('account.account', readonly=True,
                                             default=lambda self: self._default_telephone_bill_account(),
                                             string='Telephone Bill GL')

    def _default_employee_pf_contribution_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.employee_pf_contribution_account if payslip_run_obj.operating_unit_id.employee_pf_contribution_account else False

    employee_pf_contribution_account = fields.Many2one('account.account', readonly=True,
                                                       default=lambda
                                                           self: self._default_employee_pf_contribution_account(),
                                                       string='Employee PF Contribution GL')

    def _default_company_pf_contribution_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.company_pf_contribution_account if payslip_run_obj.operating_unit_id.company_pf_contribution_account else False

    company_pf_contribution_account = fields.Many2one('account.account', readonly=True,
                                                      default=lambda
                                                          self: self._default_company_pf_contribution_account(),
                                                      string='Company PF Contribution GL')

    def _default_debit_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.default_debit_account if payslip_run_obj.operating_unit_id.default_debit_account else False

    default_debit_account = fields.Many2one('account.account', readonly=True,
                                            default=lambda self: self._default_debit_account(),
                                            string='Default Debit GL')

    def _default_debit_account_ot(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.default_debit_account_ot if payslip_run_obj.operating_unit_id.default_debit_account_ot else False

    default_debit_account_ot = fields.Many2one('account.account', readonly=True,
                                               default=lambda self: self._default_debit_account_ot(),
                                               string='Default OT Debit GL')

    def _default_festival_debit_account(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.operating_unit_id.default_festival_debit_account if payslip_run_obj.operating_unit_id.default_festival_debit_account else False

    default_festival_debit_account = fields.Many2one('account.account',
                                                     default=lambda self: self._default_festival_debit_account(),
                                                     string='Default Festival Debit GL')

    @api.model
    def default_get(self, fields):
        res = super(CreateProvision, self).default_get(fields)
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        account_journal = self.env['account.journal'].sudo().search([('code', '=', 'SPJNL')])
        res.update({'journal_id': account_journal.id})

        if payslip_run_obj.operating_unit_id.debit_account_ids:
            debit_account_lines = [(5, 0, 0)]
            for debit_account in payslip_run_obj.operating_unit_id.debit_account_ids:
                line = (0, 0, {
                    'department_id': debit_account.department_id.id,
                    'account_id': debit_account.account_id.id
                })
                debit_account_lines.append(line)
            res.update({'debit_account_ids': debit_account_lines})


        if payslip_run_obj.operating_unit_id.festival_debit_account_ids:
            bonus_debit_account_lines = [(5, 0, 0)]
            for bonus_debit_account in payslip_run_obj.operating_unit_id.festival_debit_account_ids:
                line = (0, 0, {
                    'department_id': bonus_debit_account.department_id.id,
                    'account_id': bonus_debit_account.account_id.id
                })
                bonus_debit_account_lines.append(line)
            res.update({'festival_debit_account_ids': bonus_debit_account_lines})

        return res

    debit_account_ids = fields.One2many('temp.department.account.map', 'provision_id',
                                        string="""Debit GL's""")

    festival_debit_account_ids = fields.One2many('temp.bonus.department.account.map', 'provision_id',
                                                 string="""Bonus Debit GL's""")

    journal_id = fields.Many2one('account.journal', readonly=True, required=True,
                                 string='Journal')

    def _default_date(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        datetime_obj = datetime.strptime(payslip_run_obj.date_end, OE_DFORMAT)
        next_month = datetime_obj.date().replace(day=28) + timedelta(days=4)

        return next_month - timedelta(days=next_month.day)

    date = fields.Date(required=True,
                       default=lambda self: self._default_date())

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)

    def _default_company(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        if self.env.user.company_id.id != payslip_run_obj.operating_unit_id.company_id.id:
            raise UserError(_('User default company and operating unit company not matched. Change company from '
                              'selection !'))
        return payslip_run_obj.operating_unit_id.company_id

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self._default_company()
    )

    def _default_salary_type(self):
        payslip_run_obj = self.env['hr.payslip.run'].browse(self.env.context.get(
            'active_id'))
        return payslip_run_obj.type

    salary_type = fields.Selection([("0", "Regular Salary"),
                                    ("1", "Festival Bonus"),
                                    ("2", "OT")], "Type", default=lambda self: self._default_salary_type())

    def get_payslip_list(self, payslip_run_id):
        self.env.cr.execute("""
                               select id from hr_payslip where payslip_run_id = %s
                           """ % (payslip_run_id.id))
        payslip_list = []
        for id in self.env.cr.fetchall():
            payslip_list.append(self.env['hr.payslip'].browse(id))
        return payslip_list

    def get_department_net_values(self, top_sheet, code):

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
                if line.appears_on_payslip and line.code == code:
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
                            if line.appears_on_payslip and line.code == code:
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

    def get_one_cost_center_department_bill(self, cost_center, top_sheet, code, department):
        employee_list = []
        sum = 0
        for rec in top_sheet.slip_ids:
            if rec.employee_id.cost_center_id.id == cost_center.id and rec.employee_id.department_id.id == department.id:
                employee_list.append(rec.employee_id)
                for line in rec.line_ids:
                    if line.code == code:
                        sum = sum + math.ceil(line.total)
        return sum

    def get_a_cost_center_three_bill(self, cost_center, top_sheet, code1, code2, code3, department):

        # 'LOAN', 'MESS', 'MOBILE'
        employee_list = []
        loan_sum = 0
        mess_sum = 0
        mobile_sum = 0
        for rec in top_sheet.slip_ids:
            if rec.employee_id.cost_center_id.id == cost_center.id and rec.employee_id.department_id.id == department.id:
                employee_list.append(rec.employee_id)
                for line in rec.line_ids:
                    if line.code == code1:
                        loan_sum = loan_sum + math.ceil(line.total)
                    elif line.code == code2:
                        mess_sum = mess_sum + math.ceil(line.total)
                    elif line.code == code3:
                        mobile_sum = mobile_sum + math.ceil(line.total)

        return [loan_sum, mess_sum, mobile_sum]

    def get_cost_center_wise_bills(self, payslip_cost_centers, top_sheet, code, payslip_departments):
        cost_center_wise_bill_dict = OrderedDict()
        for cost_center in payslip_cost_centers:
            cost_center_wise_bill_dict[cost_center.id] = {}
            # cost_center_telephone_dict[cost_center.id]['vals'] = 0
            for department in payslip_departments:
                cost_center_wise_bill_dict[cost_center.id][department.id] = 0

        for cost_center in payslip_cost_centers:
            # cost_center_bill = self.get_one_cost_center_department_bill(cost_center, top_sheet, code)
            # cost_center_wise_bill_dict[cost_center.id]['vals'] = cost_center_bill
            for department in payslip_departments:
                cost_center_bill = self.get_one_cost_center_department_bill(cost_center, top_sheet, code, department)
                cost_center_wise_bill_dict[cost_center.id][department.id] = cost_center_bill

        return cost_center_wise_bill_dict

    def get_cost_center_wise_three_bills(self, is_ctg, payslip_cost_centers, top_sheet, code1, code2, code3,
                                         payslip_departments):
        cost_center_wise_bill_dict = OrderedDict()
        for cost_center in payslip_cost_centers:
            cost_center_wise_bill_dict[cost_center.id] = {}
            for department in payslip_departments:
                cost_center_wise_bill_dict[cost_center.id][department.id] = 0

        for cost_center in payslip_cost_centers:
            for department in payslip_departments:
                if is_ctg == 'ctg':
                    cost_center_bills = self.get_a_cost_center_three_bill(cost_center, top_sheet, code1, '', code3,
                                                                          department)

                else:
                    cost_center_bills = self.get_a_cost_center_three_bill(cost_center, top_sheet, code1, code2, code3,
                                                                          department)

                total_loan_mess_mobile_bill = 0
                for cost_center_bill in cost_center_bills:
                    total_loan_mess_mobile_bill = total_loan_mess_mobile_bill + cost_center_bill
                cost_center_wise_bill_dict[cost_center.id][department.id] = total_loan_mess_mobile_bill

        return cost_center_wise_bill_dict

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
            # 'company_id': company_id,
        }

    def create_provision(self):
        if self.payslip_run_id:
            # check if journal entry created for this payslip run
            if self.payslip_run_id.account_move_id:
                raise UserError(_('Journal Entry already created for this payslip batch.'))
            payslip_departments = self.get_departments(self.payslip_run_id)
            payslip_cost_centers = self.get_cost_centers(self.payslip_run_id)
            top_sheet_total_net_value = self.get_top_sheet_total_net_value(self.payslip_run_id)

            journal_id = self.env['account.journal'].sudo().search([('code', '=', 'SPJNL')])
            month = datetime.strptime(self.date, '%Y-%m-%d').strftime("%B")
            datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')

            if self.salary_type == '0':
                # regular salary
                department_net_values = self.get_department_net_values(self.payslip_run_id, 'NET')

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

                cost_center_wise_telephone_bill = self.get_cost_center_wise_bills(payslip_cost_centers,
                                                                                  self.payslip_run_id, 'MOBILE',
                                                                                  payslip_departments)

                # get tds, pf, loan mess mobile bill debit values
                cost_center_wise_tds = self.get_cost_center_wise_bills(payslip_cost_centers, self.payslip_run_id, 'TDS',
                                                                       payslip_departments)
                cost_center_wise_pfs = self.get_cost_center_wise_bills(payslip_cost_centers, self.payslip_run_id,
                                                                       'EPMF', payslip_departments)

                cost_center_wise_loan_mess_mobile = self.get_cost_center_wise_three_bills('', payslip_cost_centers,
                                                                                          self.payslip_run_id,
                                                                                          'LOAN', 'MESS', 'MOBILE',
                                                                                          payslip_departments)

                cost_center_wise_loan_mess_mobile_ctg = self.get_cost_center_wise_three_bills('ctg',
                                                                                              payslip_cost_centers,
                                                                                              self.payslip_run_id,
                                                                                              'LOAN', 'MESS', 'MOBILE',
                                                                                              payslip_departments)

                if self.payslip_run_id.operating_unit_id:

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
                                                                 self.payslip_run_id.operating_unit_id.id, 0, False,
                                                                 False,
                                                                 company_pf_contribution,
                                                                 self.operating_unit_id.company_id.id)

                    sum_credit = sum_credit + company_pf_contribution

                    pf_emp_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                 self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                                                                 self.payslip_run_id.operating_unit_id.id, 0, False,
                                                                 False,
                                                                 employee_pf_contribution,
                                                                 self.operating_unit_id.company_id.id)

                    sum_credit = sum_credit + employee_pf_contribution

                    if self.payslip_run_id.operating_unit_id.debit_account_ids:
                        for key, value in department_net_values.items():
                            for cost_center_value in value:
                                department = self.get_department_id(payslip_departments, key)
                                debit_account_obj = self.env['department.account.map'].sudo().search(
                                    [('department_id', '=', department.id), ('type', '=', 'regular'),
                                     ('operating_unit_id', '=', self.payslip_run_id.operating_unit_id.id)])
                                if debit_account_obj:
                                    debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                         debit_account_obj.account_id.id,
                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                         department.id, cost_center_value.id,
                                                                         department_net_values[key][cost_center_value],
                                                                         0,
                                                                         self.operating_unit_id.company_id.id)

                                else:
                                    debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                         self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                         department.id, cost_center_value.id,
                                                                         department_net_values[key][cost_center_value],
                                                                         0,
                                                                         self.operating_unit_id.company_id.id)

                                sum_debit = sum_debit + department_net_values[key][cost_center_value]

                                if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                    move_lines.append((0, 0, debit_vals))

                        # tds debit
                        for key, value in cost_center_wise_tds.items():
                            for department in payslip_departments:
                                if value[department.id] < 0:
                                    value[department.id] = value[department.id] * (-1)
                                if not value[department.id] == 0:
                                    tds_debit_values = self.get_move_line_vals('TDS', self.date, journal_id.id,
                                                                               self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                               self.payslip_run_id.operating_unit_id.id,
                                                                               department.id,
                                                                               key,
                                                                               value[department.id],
                                                                               0,
                                                                               self.operating_unit_id.company_id.id)

                                    sum_debit = sum_debit + value[department.id]
                                    move_lines.append((0, 0, tds_debit_values))

                        # pfs debit
                        for key, value in cost_center_wise_pfs.items():
                            for department in payslip_departments:
                                if value[department.id] < 0:
                                    value[department.id] = value[department.id] * (-1)
                                if not value[department.id] == 0:
                                    pfs_debit_values = self.get_move_line_vals('PF', self.date,
                                                                               journal_id.id,
                                                                               self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                               self.payslip_run_id.operating_unit_id.id,
                                                                               department.id,
                                                                               key,
                                                                               value[department.id] * 2,
                                                                               0,
                                                                               self.operating_unit_id.company_id.id)

                                    sum_debit = sum_debit + value[department.id] * 2
                                    move_lines.append((0, 0, pfs_debit_values))

                        if not self.payslip_run_id.operating_unit_id.code == 'SCCL-CTG':
                            # loan mess mobile debit
                            for key, value in cost_center_wise_loan_mess_mobile.items():
                                for department in payslip_departments:
                                    if value[department.id] < 0:
                                        value[department.id] = value[department.id] * (-1)
                                    if not value[department.id] == 0:
                                        loan_mess_debit_values = self.get_move_line_vals('Loan, Mess and Mobile Bill',
                                                                                         self.date, journal_id.id,
                                                                                         self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                                         department.id,
                                                                                         key,
                                                                                         value[department.id],
                                                                                         0,
                                                                                         self.operating_unit_id.company_id.id)

                                        sum_debit = sum_debit + value[department.id]
                                        move_lines.append((0, 0, loan_mess_debit_values))

                        else:
                            # loan mess mobile debit
                            for key, value in cost_center_wise_loan_mess_mobile_ctg.items():
                                for department in payslip_departments:
                                    if value[department.id] < 0:
                                        value[department.id] = value[department.id] * (-1)
                                    if not value[department.id] == 0:
                                        loan_mess_debit_values = self.get_move_line_vals('Loan and Mobile Bill',
                                                                                         self.date, journal_id.id,
                                                                                         self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                                         department.id,
                                                                                         key,
                                                                                         value[department.id],
                                                                                         0,
                                                                                         self.operating_unit_id.company_id.id)

                                        sum_debit = sum_debit + value[department.id]
                                        move_lines.append((0, 0, loan_mess_debit_values))

                        total_telephone_credit_vals = 0
                        for key, value in cost_center_wise_telephone_bill.items():
                            for department in payslip_departments:
                                if value[department.id] < 0:
                                    value[department.id] = value[department.id] * (-1)
                                if not value[department.id] == 0:
                                    telephone_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                                    self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                                                                                    self.payslip_run_id.operating_unit_id.id,
                                                                                    department.id,
                                                                                    key,
                                                                                    0,
                                                                                    value[department.id],
                                                                                    self.operating_unit_id.company_id.id)

                                    move_lines.append((0, 0, telephone_credit_vals))
                                    total_telephone_credit_vals = total_telephone_credit_vals + value[department.id]

                        sum_credit = sum_credit + total_telephone_credit_vals

                        main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                   self.payslip_run_id.operating_unit_id.payable_account.id,
                                                                   self.payslip_run_id.operating_unit_id.id, False,
                                                                   False,
                                                                   0, sum_debit - sum_credit,
                                                                   self.operating_unit_id.company_id.id)

                        move_lines.append((0, 0, tds_credit_vals))
                        move_lines.append((0, 0, pf_com_credit_vals))
                        move_lines.append((0, 0, pf_emp_credit_vals))
                        move_lines.append((0, 0, main_credit_vals))
                        sum_credit = sum_credit + sum_debit - sum_credit
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

                            # tds debit
                            for key, value in cost_center_wise_tds.items():
                                for department in payslip_departments:
                                    if value[department.id] < 0:
                                        value[department.id] = value[department.id] * (-1)
                                    if not value[department.id] == 0:
                                        tds_debit_values = self.get_move_line_vals('TDS', self.date, journal_id.id,
                                                                                   self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                                   self.payslip_run_id.operating_unit_id.id,
                                                                                   department.id,
                                                                                   key,
                                                                                   value[department.id],
                                                                                   0,
                                                                                   self.operating_unit_id.company_id.id)

                                        sum_debit = sum_debit + value[department.id]
                                        move_lines.append((0, 0, tds_debit_values))

                            # pfs debit
                            for key, value in cost_center_wise_pfs.items():
                                for department in payslip_departments:
                                    if value[department.id] < 0:
                                        value[department.id] = value[department.id] * (-1)
                                    if not value[department.id] == 0:
                                        pfs_debit_values = self.get_move_line_vals('PF', self.date,
                                                                                   journal_id.id,
                                                                                   self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                                   self.payslip_run_id.operating_unit_id.id,
                                                                                   department.id,
                                                                                   key,
                                                                                   value[department.id] * 2,
                                                                                   0,
                                                                                   self.operating_unit_id.company_id.id)

                                        sum_debit = sum_debit + value[department.id] * 2
                                        move_lines.append((0, 0, pfs_debit_values))

                            if not self.payslip_run_id.operating_unit_id.code == 'SCCL-CTG':
                                # loan mess mobile debit
                                for key, value in cost_center_wise_loan_mess_mobile.items():
                                    for department in payslip_departments:
                                        if value[department.id] < 0:
                                            value[department.id] = value[department.id] * (-1)
                                        if not value[department.id] == 0:
                                            loan_mess_debit_values = self.get_move_line_vals(
                                                'Loan, Mess and Mobile Bill',
                                                self.date, journal_id.id,
                                                self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                self.payslip_run_id.operating_unit_id.id,
                                                department.id,
                                                key,
                                                value[department.id],
                                                0,
                                                self.operating_unit_id.company_id.id)

                                            sum_debit = sum_debit + value[department.id]
                                            move_lines.append((0, 0, loan_mess_debit_values))

                            else:
                                # loan mess mobile debit
                                for key, value in cost_center_wise_loan_mess_mobile_ctg.items():
                                    for department in payslip_departments:
                                        if value[department.id] < 0:
                                            value[department.id] = value[department.id] * (-1)
                                        if not value[department.id] == 0:
                                            loan_mess_debit_values = self.get_move_line_vals('Loan and Mobile Bill',
                                                                                             self.date, journal_id.id,
                                                                                             self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                                             self.payslip_run_id.operating_unit_id.id,
                                                                                             department.id,
                                                                                             key,
                                                                                             value[department.id],
                                                                                             0,
                                                                                             self.operating_unit_id.company_id.id)

                                            sum_debit = sum_debit + value[department.id]
                                            move_lines.append((0, 0, loan_mess_debit_values))

                            total_telephone_credit_vals = 0
                            for key, value in cost_center_wise_telephone_bill.items():
                                for department in payslip_departments:
                                    if value[department.id] < 0:
                                        value[department.id] = value[department.id] * (-1)
                                    if not value[department.id] == 0:
                                        telephone_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                                        self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                                                                                        self.payslip_run_id.operating_unit_id.id,
                                                                                        department.id,
                                                                                        key,
                                                                                        0,
                                                                                        value[department.id],
                                                                                        self.operating_unit_id.company_id.id)

                                        move_lines.append((0, 0, telephone_credit_vals))
                                        total_telephone_credit_vals = total_telephone_credit_vals + value[department.id]

                            sum_credit = sum_credit + total_telephone_credit_vals

                            main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                       self.payslip_run_id.operating_unit_id.payable_account.id,
                                                                       self.payslip_run_id.operating_unit_id.id, False,
                                                                       False,
                                                                       0, sum_debit - sum_credit,
                                                                       self.operating_unit_id.company_id.id)

                            move_lines.append((0, 0, tds_credit_vals))
                            move_lines.append((0, 0, pf_com_credit_vals))
                            move_lines.append((0, 0, pf_emp_credit_vals))
                            move_lines.append((0, 0, main_credit_vals))
                            sum_credit = sum_credit + sum_debit - sum_credit

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
                        if len(move_lines) > 0:
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
                                'ref': 'Total net value : ' + str(top_sheet_total_net_value) + '\n' + 'Batch : ' + str(
                                    self.payslip_run_id.name)
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
                            raise UserError(
                                _('Could not create journal entry! There may have some problem in your payslips.'))

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
                            'ref': 'Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. ' % difference + '\n' + 'Batch : ' + str(
                                self.payslip_run_id.name)

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
            elif self.salary_type == '1':
                festival_department_net_values = self.get_department_net_values(self.payslip_run_id, 'FBONUS')
                if self.payslip_run_id.operating_unit_id:
                    move_lines = []
                    sum_debit = 0

                    if self.payslip_run_id.operating_unit_id.festival_debit_account_ids:
                        for key, value in festival_department_net_values.items():
                            for cost_center_value in value:
                                department = self.get_department_id(payslip_departments, key)
                                debit_account_obj = self.env['department.account.map'].sudo().search(
                                    [('department_id', '=', department.id), ('type', '=', 'festival_bonus')])
                                if debit_account_obj:
                                    debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                         debit_account_obj.account_id.id,
                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                         department.id, cost_center_value.id,
                                                                         festival_department_net_values[key][
                                                                             cost_center_value],
                                                                         0,
                                                                         self.operating_unit_id.company_id.id)

                                else:
                                    debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                         self.payslip_run_id.operating_unit_id.default_festival_debit_account.id,
                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                         department.id, cost_center_value.id,
                                                                         festival_department_net_values[key][
                                                                             cost_center_value],
                                                                         0,
                                                                         self.operating_unit_id.company_id.id)

                                sum_debit = sum_debit + festival_department_net_values[key][cost_center_value]

                                if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                    move_lines.append((0, 0, debit_vals))

                        main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                   self.payslip_run_id.operating_unit_id.payable_account.id,
                                                                   self.payslip_run_id.operating_unit_id.id, False,
                                                                   False,
                                                                   0, sum_debit,
                                                                   self.operating_unit_id.company_id.id)

                        move_lines.append((0, 0, main_credit_vals))
                        sum_credit = sum_debit
                    else:
                        if self.payslip_run_id.operating_unit_id.default_festival_debit_account:
                            for key, value in festival_department_net_values.items():
                                for cost_center_value in value:
                                    department = self.get_department_id(payslip_departments, key)

                                    debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                         self.payslip_run_id.operating_unit_id.default_festival_debit_account.id,
                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                         department.id, cost_center_value.id,
                                                                         festival_department_net_values[key][
                                                                             cost_center_value], 0,
                                                                         self.operating_unit_id.company_id.id)

                                    sum_debit = sum_debit + festival_department_net_values[key][cost_center_value]

                                    if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                        move_lines.append((0, 0, debit_vals))

                            main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                       self.payslip_run_id.operating_unit_id.payable_account.id,
                                                                       self.payslip_run_id.operating_unit_id.id, False,
                                                                       False,
                                                                       0, sum_debit,
                                                                       self.operating_unit_id.company_id.id)

                            move_lines.append((0, 0, main_credit_vals))
                            sum_credit = sum_debit

                    name_seq = self.env['ir.sequence'].next_by_code('account.move.seq')
                    difference = 0

                    if difference == 0:
                        if len(move_lines) > 0:
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
                                'ref': 'Total net value : ' + str(
                                    top_sheet_total_net_value) + '\n' + 'Batch : ' + str(
                                    self.payslip_run_id.name)
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
                            raise UserError(
                                _('Could not create journal entry! There may have some problem in your payslips.'))

            elif self.salary_type == '2':
                ot_department_net_values = self.get_department_net_values(self.payslip_run_id, 'EOTA')
                if self.payslip_run_id.operating_unit_id:
                    move_lines = []
                    sum_debit = 0

                    if self.payslip_run_id.operating_unit_id.default_debit_account_ot:
                        for key, value in ot_department_net_values.items():
                            for cost_center_value in value:
                                department = self.get_department_id(payslip_departments, key)
                                if ot_department_net_values[key][cost_center_value] != 0:
                                    debit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                         self.payslip_run_id.operating_unit_id.default_debit_account_ot.id,
                                                                         self.payslip_run_id.operating_unit_id.id,
                                                                         department.id, cost_center_value.id,
                                                                         ot_department_net_values[key][
                                                                             cost_center_value], 0,
                                                                         self.operating_unit_id.company_id.id)

                                    sum_debit = sum_debit + ot_department_net_values[key][cost_center_value]

                                    if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                        move_lines.append((0, 0, debit_vals))

                        main_credit_vals = self.get_move_line_vals('0', self.date, journal_id.id,
                                                                   self.payslip_run_id.operating_unit_id.payable_account_ot.id,
                                                                   self.payslip_run_id.operating_unit_id.id, False,
                                                                   False,
                                                                   0, sum_debit,
                                                                   self.operating_unit_id.company_id.id)

                        move_lines.append((0, 0, main_credit_vals))
                        sum_credit = sum_debit

                    name_seq = self.env['ir.sequence'].next_by_code('account.move.seq')
                    difference = 0

                    if difference == 0:
                        if len(move_lines) > 0:
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
                                'ref': 'Total net value : ' + str(
                                    top_sheet_total_net_value) + '\n' + 'Batch : ' + str(
                                    self.payslip_run_id.name)
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
                            raise UserError(_('Could not create journal entry! There may have some problem in your payslips.'))

            else:
                raise UserError(_('Salary type not found'))
        else:
            raise UserError(_('Payslip Batch not found!'))
