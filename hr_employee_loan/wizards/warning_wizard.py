from odoo import models, fields, api


class HrLoanApplyWarning(models.TransientModel):

    _name = "hr.employee.loan.apply.warning"

    @api.multi
    def action_apply(self):
        form_id = self.env.context.get('active_id')
        loan = self.env['hr.employee.loan'].search([('id', '=', form_id)])
        loan.action_apply(loan)

class HrLoanApproveWarning(models.TransientModel):

    _name = "hr.employee.loan.approve.warning"

    @api.multi
    def action_approve(self):
        form_id = self.env.context.get('active_id')
        loan = self.env['hr.employee.loan'].search([('id', '=', form_id)])
        loan.action_approve(loan)