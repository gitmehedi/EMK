from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InheritedPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)
    account_move_id = fields.Many2one('account.move', readonly=True, string='Journal Entry')

    def get_journal_entry(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.account_move_id.id)],
            'context': "{'create': False}"
        }

    @api.multi
    def create_provision(self):

        if self.account_move_id:
            raise UserError(_('Journal Entry already created for this payslip batch.'))

        if self.operating_unit_id:
            if not self.operating_unit_id.payable_account:
                raise UserError(_('GL Mapping not configured for this operating unit for payable account.'))
            elif not self.operating_unit_id.tds_payable_account:
                raise UserError(_('GL Mapping not configured for this operating unit for tds payable account.'))
            elif not self.operating_unit_id.telephone_bill_account:
                raise UserError(_('GL Mapping not configured for this operating unit for telephone bill account.'))
            elif not self.operating_unit_id.employee_pf_contribution_account:
                raise UserError(
                    _('GL Mapping not configured for this operating unit for employee contribution account.'))
            elif not self.operating_unit_id.company_pf_contribution_account:
                raise UserError(
                    _('GL Mapping not configured for this operating unit for company contribution account.'))
            elif not self.operating_unit_id.default_debit_account:
                raise UserError(_('GL Mapping not configured for this operating unit for default debit account.'))

        no_cost_center_employee_list = []
        no_department_employee_list = []
        no_operating_unit_employee_list = []
        for slip in self.slip_ids:
            if not slip.employee_id.cost_center_id:
                no_cost_center_employee_list.append(slip.employee_id.name + ', ')
            if not slip.employee_id.department_id:
                no_department_employee_list.append(slip.employee_id.name + ', ')
            if not slip.employee_id.operating_unit_id:
                no_operating_unit_employee_list.append(slip.employee_id.name + ', ')
        if no_cost_center_employee_list:
            raise UserError(_('Cannot create journal entry because these employees (%s) does not have cost center '
                              'configured.' % no_cost_center_employee_list))

        if no_department_employee_list:
            raise UserError(_('Cannot create journal entry because these employees (%s) does not have department '
                              'configured.' % no_department_employee_list))

        if no_operating_unit_employee_list:
            raise UserError(_('Cannot create journal entry because these employees (%s) does not have operating unit '
                              'configured.' % no_operating_unit_employee_list))
        return {
            'res_model': 'hr.payslip.run.create.provision',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("gbs_hr_payroll_accounting_automation.create_provision_form_view").id

        }
