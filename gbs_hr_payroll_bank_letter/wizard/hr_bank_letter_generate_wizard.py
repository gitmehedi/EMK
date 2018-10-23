from odoo import models, fields, api
import datetime

class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.bank.selection.wizard'

    bank_names = fields.Many2one('res.partner.bank', string="Select A Bank Account", required=True,
                                 domain=[('is_payroll_account', '=', True)])

    @api.multi
    def process_print(self):

        payslip_run_pool = self.env['hr.payslip.run']
        docs = payslip_run_pool.browse([self._context['active_id']])
        now = datetime.datetime.now()
 
        data = {}
        data['bank_id'] = self.bank_names.bank_id.id
        data['bank_name'] = self.bank_names.bank_id.name
        data['bank_street1'] = self.bank_names.bank_id.street
        data['bank_street2'] = self.bank_names.bank_id.street2
        data['bank_city'] = self.bank_names.bank_id.city
        data['bank_zip'] = self.bank_names.bank_id.zip
        data['bank_country'] = self.bank_names.bank_id.country.name
        data['payslip_report_name'] = docs.name
        data['active_id'] = self._context['active_id']
        data['cur_year'] = now.year
        data['cur_month'] = now.strftime("%B")
        data['cur_day'] = now.day
        data['mother_bank_ac'] = self.bank_names.acc_number
 
        return self.env['report'].get_action(self, 'gbs_hr_payroll_bank_letter.report_individual_payslip1', data=data)
