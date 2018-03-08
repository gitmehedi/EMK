from odoo import api, fields, models, tools, _
import datetime
from odoo.exceptions import UserError

class InheritResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    is_payroll_account = fields.Boolean(string='Payroll A/C', default=False)


class HrPayrollAdvice(models.Model):

    _inherit = 'hr.payroll.advice'

    bank_acc_id = fields.Many2one('res.partner.bank', "Bank Account")


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        active_id = self.env.context.get('active_id')

        res = super(HrPayslipEmployees, self).compute_sheet()

        payslip_run = self.env['hr.payslip.run'].browse(active_id)
        for payslip in payslip_run.slip_ids:
            payslip.onchange_employee()
            payslip.compute_sheet()
            if not payslip.contract_id:
                payslip.unlink()

        return res


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def confirm_payslip(self):
        res = super(HrPayslipRun, self).close_payslip_run()

        for payslip in self.slip_ids:
            payslip.action_payslip_done()

        return res

    @api.multi
    def create_advice(self):
        for run in self:
            if run.available_advice:
                raise UserError(
                    _("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") % (run.name,))
            company = self.env.user.company_id

            ## Prepare the Bank Arrays
            banks = []
            for slip in run.slip_ids:
                if slip.employee_id.bank_account_id and slip.employee_id.bank_account_id.bank_id:
                    if slip.employee_id.bank_account_id.bank_id.id not in banks:
                        banks.append(slip.employee_id.bank_account_id.bank_id.id)

            ### Create Payment Advice
            for bank in banks:
                ### Set Bank Account
                bank_accs = self.env['res.partner.bank'].search([('bank_id','=',bank),
                                                                ('is_payroll_account','=',True)])
                if not bank_accs:
                    raise UserError(_('Please define payroll bank account.'))
                else:
                    bank_acc_id = bank_accs[0].id
                #################################
                advice = self.env['hr.payroll.advice'].create({
                    'batch_id': run.id,
                    'company_id': company.id,
                    'name': run.name,
                    'date': run.date_end,
                    'bank_id': bank,
                    'bank_acc_id': bank_acc_id
                })

                ### Create Advice Line
                for slip in run.slip_ids:
                    slip.action_payslip_done()
                    # if not slip.employee_id.bank_account_id or not slip.employee_id.bank_account_id.acc_number:
                    #     raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name))

                    if slip.employee_id.bank_account_id and slip.employee_id.bank_account_id.bank_id and slip.employee_id.bank_account_id.acc_number:
                        if bank == slip.employee_id.bank_account_id.bank_id.id:
                            payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                            if payslip_line:
                                self.env['hr.payroll.advice.line'].create({
                                    'advice_id': advice.id,
                                    'name': slip.employee_id.bank_account_id.acc_number,
                                    'ifsc_code': slip.employee_id.bank_account_id.bank_bic or '',
                                    'employee_id': slip.employee_id.id,
                                    'bysal': payslip_line.total
                                })

        self.write({'available_advice': True})







class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    days_in_period= fields.Integer('Days in Period', compute= '_compute_days',
                                   store= True)

    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for payslip in self:
            if payslip.date_from and payslip.date_to:
                start = datetime.datetime.strptime(payslip.date_from, "%Y-%m-%d").date()
                end = datetime.datetime.strptime(payslip.date_to, "%Y-%m-%d").date()
                payslip.days_in_period = (((end - start).days)) + 1

    @api.multi
    def action_compute_payslip(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for payslip in self.browse(active_ids):
            payslip.compute_sheet()


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    days_in_period = fields.Integer('Days in Period', related='payslip_id.days_in_period')
