from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class LetterCreditReport(models.TransientModel):
    _name = 'letter.credit.wizard'
    _description = 'Letter of Credit Report'

    report_type = fields.Selection([
        ('Active', "Active"),
        ('Done', "Done"),
        ('Cancel', "Cancel")],string='Select')

    @api.multi
    def process_report(self):
        data = {}

        data['report_type'] = self.report_type


        return self.env['report'].get_action(self, 'letter_of_credit_report.template_letter_of_credit_report', data=data)
