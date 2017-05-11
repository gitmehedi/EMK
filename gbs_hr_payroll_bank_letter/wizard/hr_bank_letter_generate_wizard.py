from openerp import models, fields, api

class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.bank.selection.wizard'

    bank_names = fields.Many2one('res.bank', string="Banks", required=True)

    @api.multi
    def process_print(self):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse([self._context['active_id']])

        data = {}
        data['bank_id'] = self.bank_names.id
        data['bank_name'] = self.bank_names.name
        data['active_id'] = self._context['active_id']

        return self.env['report'].get_action(self, 'gbs_hr_payroll_bank_letter.report_individual_payslip1', data=data)

