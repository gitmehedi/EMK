from odoo import api, fields, models, tools, _
#from datetime import date
#from datetime import datetime
import datetime
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
            payslip.action_payslip_done_with_loan()

        return res

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    days_in_period= fields.Integer('Days in Period', compute= '_compute_days',
                                   store= True, required=True)

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
