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
        else:
            print('not debit accounts found')
        return res

    debit_account_ids = fields.One2many('temp.department.account.map', 'provision_id',
                                        string="""Debit GL's""")

    journal_id = fields.Many2one('account.journal', readonly=True, required=True,
                                 string='Journal')
    date = fields.Date(required=True, default=fields.Date.context_today)

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

    def get_department_id(self, payslip_departments, key):
        for department in payslip_departments:
            if department.name == key:
                return department

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

    def get_move_line_vals(self, name, move_id, date, journal_id, account_id, operating_unit_id, department_id,
                           cost_center_id,
                           debit, credit,
                           company_id):
        return {
            'name': name,
            'move_id': move_id,
            'date': date,
            'journal_id': journal_id,
            'account_id': account_id,
            'operating_unit_id': operating_unit_id,
            'department_id': department_id,
            'cost_center_id': cost_center_id,
            'debit': debit,
            'credit': credit
        }

    def get_department_cost_center_net(self, cost_center_id, department_id, topsheet):
        department_costcenter_net = 0
        for slip in topsheet.slip_ids:
            if slip.employee_id.cost_center_id.id == cost_center_id:
                if slip.employee_id.department_id.id == department_id:
                    for line in slip.line_ids:
                        if line.appears_on_payslip and line.code == 'NET':
                            department_costcenter_net = department_costcenter_net + math.ceil(line.total)

        return department_costcenter_net

    def get_cost_center_wise_telephone_bill(self, payslip_cost_centers, cost_center_telephone_dict, topsheet):
        for cost_center in payslip_cost_centers:
            cost_center_telephone_bill = self.get_a_cost_center_telephone_bill(cost_center, topsheet)
            cost_center_telephone_dict[cost_center.id]['vals'] = cost_center_telephone_bill
        return cost_center_telephone_dict

    @api.multi
    def create_provision(self):
        if self.payslip_run_id:
            # check if journal entry created for this payslip run
            if self.payslip_run_id.account_move_id:
                raise UserError(_('Journal Entry already created for this payslip batch.'))

            topsheet = self.payslip_run_id
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            month = datetime.strptime(self.date, '%Y-%m-%d').strftime("%B")
            datey = datetime.strptime(self.date, '%Y-%m-%d').strftime('%Y')
            journal_id = self.env['account.journal'].sudo().search([('code', '=', 'SPJNL')])
            name_seq = self.env['ir.sequence'].next_by_code('account.move.seq')

            departments = []
            cost_centers = []
            record = OrderedDict()

            top_sheet_total_net_value = 0
            total_tax_deducted_source = 0
            employee_pf_contribution = 0
            telephone_mobile_bill = 0

            for slip in topsheet.slip_ids:
                if not slip.employee_id.cost_center_id:
                    raise UserError(_('Cannot create journal entry because employee does not have cost center '
                                      'configured.'))
                if not slip.employee_id.department_id:
                    raise UserError(_('Cannot create journal entry because employee does not have department '
                                      'configured.'))
                if not slip.employee_id.operating_unit_id:
                    raise UserError(_('Cannot create journal entry because employee does not have operating unit '
                                      'configured.'))
                departments.append(slip.employee_id.department_id)
                cost_centers.append(slip.employee_id.cost_center_id)

                for line in slip.line_ids:
                    if line.appears_on_payslip and line.code == 'NET':
                        top_sheet_total_net_value = top_sheet_total_net_value + math.ceil(line.total)

                    if line.appears_on_payslip and line.code == 'TDS':
                        total_tax_deducted_source = total_tax_deducted_source + math.ceil(line.total)

                    if line.appears_on_payslip and line.code == 'EPMF':
                        employee_pf_contribution = employee_pf_contribution + math.ceil(line.total)

                    if line.appears_on_payslip and line.code == 'MOBILE':
                        telephone_mobile_bill = telephone_mobile_bill + math.ceil(line.total)

                record[slip.employee_id.department_id.id] = {}
                record[slip.employee_id.department_id.id][slip.employee_id.cost_center_id.id] = 0

            payslip_departments = list(dict.fromkeys(departments))
            payslip_cost_centers = list(dict.fromkeys(cost_centers))

            cost_center_telephone_dict = OrderedDict()

            for cost_center in payslip_cost_centers:
                cost_center_telephone_dict[cost_center.id] = {}
                cost_center_telephone_dict[cost_center.id]['vals'] = 0
                for department in payslip_departments:
                    department_costcenter_net = self.get_department_cost_center_net(cost_center.id, department.id,
                                                                                    topsheet)
                    if department_costcenter_net != 0:
                        record[department.id][cost_center.id] = department_costcenter_net

            cost_center_wise_telephone_bill = self.get_cost_center_wise_telephone_bill(payslip_cost_centers,
                                                                                       cost_center_telephone_dict,
                                                                                       topsheet)

            if total_tax_deducted_source < 0:
                total_tax_deducted_source = total_tax_deducted_source * (-1)
            if employee_pf_contribution < 0:
                employee_pf_contribution = employee_pf_contribution * (-1)

            company_pf_contribution = employee_pf_contribution
            if company_pf_contribution < 0:
                company_pf_contribution = company_pf_contribution * (-1)

            if self.payslip_run_id.operating_unit_id:
                move_lines = []
                sum_debit = 0
                sum_credit = 0
                vals = {
                    'name': name_seq,
                    'journal_id': journal_id.id,
                    'operating_unit_id': self.payslip_run_id.operating_unit_id.id,
                    'date': self.date,
                    'company_id': self.company_id.id,
                    'state': 'draft',
                    'narration': 'Provision above amount against Salary month of ' + month + '-' + datey,
                    'ref': 'Total net value : ' + str(top_sheet_total_net_value)
                }
                move = self.env['account.move'].create(vals)

                tds_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                          self.payslip_run_id.operating_unit_id.tds_payable_account.id,
                                                          self.payslip_run_id.operating_unit_id.id, False, False, 0,
                                                          total_tax_deducted_source,
                                                          self.operating_unit_id.company_id.id)

                sum_credit = sum_credit + total_tax_deducted_source

                pf_com_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                             self.payslip_run_id.operating_unit_id.company_pf_contribution_account.id,
                                                             self.payslip_run_id.operating_unit_id.id, 0, False, False,
                                                             company_pf_contribution,
                                                             self.operating_unit_id.company_id.id)

                sum_credit = sum_credit + company_pf_contribution

                pf_emp_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                             self.payslip_run_id.operating_unit_id.employee_pf_contribution_account.id,
                                                             self.payslip_run_id.operating_unit_id.id, 0, False, False,
                                                             employee_pf_contribution,
                                                             self.operating_unit_id.company_id.id)

                sum_credit = sum_credit + employee_pf_contribution

                if self.payslip_run_id.operating_unit_id.debit_account_ids:
                    for key, value in record.items():
                        for cost_center_value in value:
                            # department = self.get_department_id(payslip_departments, key)
                            debit_account_obj = self.env['department.account.map'].sudo().search(
                                [('department_id', '=', key),
                                 ('operating_unit_id', '=', self.payslip_run_id.operating_unit_id.id)])
                            if debit_account_obj:
                                debit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                                     debit_account_obj.account_id.id,
                                                                     self.payslip_run_id.operating_unit_id.id,
                                                                     key, cost_center_value,
                                                                     record[key][cost_center_value], 0,
                                                                     self.operating_unit_id.company_id.id)

                            else:
                                debit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                                     self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                     self.payslip_run_id.operating_unit_id.id,
                                                                     key, cost_center_value,
                                                                     record[key][cost_center_value], 0,
                                                                     self.operating_unit_id.company_id.id)

                            sum_debit = sum_debit + record[key][cost_center_value]

                            if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                move_lines.append((0, 0, debit_vals))
                                aml_obj_created = aml_obj.create(debit_vals)

                    total_telephone_credit_vals = 0
                    for key, value in cost_center_wise_telephone_bill.items():
                        if value['vals'] < 0:
                            value['vals'] = value['vals'] * (-1)
                        if not value['vals'] == 0:
                            telephone_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                                            self.payslip_run_id.operating_unit_id.telephone_bill_account.id,
                                                                            self.payslip_run_id.operating_unit_id.id,
                                                                            False,
                                                                            key,
                                                                            0,
                                                                            value['vals'],
                                                                            self.operating_unit_id.company_id.id)

                            move_lines.append((0, 0, telephone_credit_vals))
                            aml_obj.create(telephone_credit_vals)
                            total_telephone_credit_vals = total_telephone_credit_vals + value['vals']
                    sum_credit = sum_credit + telephone_mobile_bill

                    main_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                               self.payslip_run_id.operating_unit_id.payable_account.id,
                                                               self.payslip_run_id.operating_unit_id.id, False, False,
                                                               0, sum_debit - (
                                                                       total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill),
                                                               self.operating_unit_id.company_id.id)

                    move_lines.append((0, 0, tds_credit_vals))
                    aml_obj.create(tds_credit_vals)
                    move_lines.append((0, 0, pf_com_credit_vals))
                    aml_obj.create(pf_com_credit_vals)
                    move_lines.append((0, 0, pf_emp_credit_vals))
                    aml_obj.create(pf_emp_credit_vals)
                    move_lines.append((0, 0, main_credit_vals))
                    aml_obj.create(main_credit_vals)
                    sum_credit = sum_credit + sum_debit - (
                            total_tax_deducted_source + company_pf_contribution + employee_pf_contribution + telephone_mobile_bill)
                else:
                    if self.payslip_run_id.operating_unit_id.default_debit_account:
                        for key, value in record.items():
                            for cost_center_value in value:
                                department = self.get_department_id(payslip_departments, key)

                                debit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
                                                                     self.payslip_run_id.operating_unit_id.default_debit_account.id,
                                                                     self.payslip_run_id.operating_unit_id.id,
                                                                     department.id, cost_center_value.id,
                                                                     record[key][cost_center_value], 0,
                                                                     self.operating_unit_id.company_id.id)

                                sum_debit = sum_debit + record[key][cost_center_value]

                                if not (debit_vals['debit'] == 0 and debit_vals['credit'] == 0):
                                    move_lines.append((0, 0, debit_vals))
                                    aml_obj_created = aml_obj.create(debit_vals)

                        total_telephone_credit_vals = 0
                        for key, value in cost_center_wise_telephone_bill.items():
                            if value['vals'] < 0:
                                value['vals'] = value['vals'] * (-1)
                            if not value['vals'] == 0:
                                telephone_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
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

                        main_credit_vals = self.get_move_line_vals('0', move.id, self.date, journal_id.id,
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

                    if move:
                        self.payslip_run_id.write({'account_move_id': move.id})
                        message_id = self.env['success.wizard'].create({'message': _(
                            "Journal Entry Created Successfully!")
                        })
                        vals = {
                            'payslip_run_id': self.payslip_run_id.id
                        }
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

                    move.write({
                        'ref': 'Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. ' % difference})

                    message_id = self.env['confirmation.wizard'].create({'message': _(
                        "Difference Between Top Sheet Net Value and Total Debit/Credit Amount is %s. Are you sure to create journal entry?" % difference)
                    })
                    vals = {
                        'created_move_id': move.id,
                    }
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
