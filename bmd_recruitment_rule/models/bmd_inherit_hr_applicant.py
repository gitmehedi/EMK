from odoo import models, fields, api
from datetime import date,datetime, timedelta



class BMDInheritedHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    applicant_age = fields.Integer(compute='_compute_applicant_age',string='Applicant Age')
    eligible = fields.Boolean(compute='_compute_eligibility', string='Eligible')

    def _compute_applicant_age(self):

        b_date = datetime.strptime(str(self.birth_date), "%Y/%m/%d")
        b_date = datetime.datetime.strptime(self.birth_date, "%Y/%m/%d")
        applicant_days = (datetime.today() - b_date).days

        # self.applicant_age = datetime.today()-datetime.strptime(self.birth_date, "%Y-%m-%d")



    @api.depends('applicant_age')
    def _compute_eligibility(self):
        min_applicable_age = 17
        max_applicable_age = 30
        ex_service_personnel = True
        if self.quota:
            max_applicable_age = 32
        elif self.divisional_candiate == 'yes':
            if self.job_id.name == 'Weather Assistant' or self.job_id.name == 'Higher Visitor':
                max_applicable_age = 35
        elif self.job_id.name == "Electrician" and ex_service_personnel == 'yes':
            max_applicable_age = 40
        if self.applicant_age <= max_applicable_age and self.applicant_age > min_applicable_age:
            self.eligible = True
        else:
            self.eligible = False



