from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        res = super(HrPayslipEmployees, self).compute_sheet()

        active_id = self.env.context.get('active_id')
        payslip_run = self.env['hr.payslip.run'].browse(active_id)

        for payslip in payslip_run.slip_ids:
            payslip.onchange_employee()
            payslip.compute_sheet()

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

    @api.multi
    def action_compute_payslip(self):
        for payslip in self:
            payslip.compute_sheet()

