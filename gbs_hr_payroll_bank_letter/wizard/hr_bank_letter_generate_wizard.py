from openerp import models, fields, api
import datetime

class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.bank.selection.wizard'

    bank_names = fields.Many2one('res.bank', string="Banks", required=True)

    @api.multi
    def process_print(self):
        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse([self._context['active_id']])
        now = datetime.datetime.now()

        data = {}
        data['bank_id'] = self.bank_names.id
        data['bank_name'] = self.bank_names.name
        data['bank_street1'] = self.bank_names.street
        data['bank_street2'] = self.bank_names.street2
        data['bank_city'] = self.bank_names.city
        data['bank_zip'] = self.bank_names.zip
        data['bank_country'] = self.bank_names.country.name
        data['payslip_report_name'] = docs.name
        data['active_id'] = self._context['active_id']
        data['cur_year'] = now.year
        data['cur_month'] = now.strftime("%B")
        data['cur_day'] = now.day



        return self.env['report'].get_action(self, 'gbs_hr_payroll_bank_letter.report_individual_payslip1', data=data)

