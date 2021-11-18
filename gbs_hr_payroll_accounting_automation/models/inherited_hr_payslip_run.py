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
        payslip_run = self.env['hr.payslip.run'].sudo().browse(self.id)
        entry_exist = payslip_run.search([('account_move_id', '!=', False)])

        if self.account_move_id:
            raise UserError(_('Journal Entry already created for this payslip batch.'))

        for slip in self.slip_ids:
            if not slip.employee_id.cost_center_id:
                raise UserError(_('Cannot create journal entry because employee does not have cost center '
                                  'configured.'))
            if not slip.employee_id.department_id:
                raise UserError(_('Cannot create journal entry because employee does not have department '
                                  'configured.'))
            if not slip.employee_id.operating_unit_id:
                raise UserError(_('Cannot create journal entry because employee does not have operating unit '
                                  'configured.'))

        return {
            # 'name': self.order_id,
            'res_model': 'hr.payslip.run.create.provision',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("gbs_hr_payroll_accounting_automation.create_provision_form_view").id

        }
