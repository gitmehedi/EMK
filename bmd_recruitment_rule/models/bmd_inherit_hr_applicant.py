from odoo import models, fields, api
from datetime import date,datetime, timedelta


class BMDInheritedHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    applicant_age = fields.Integer(compute='_compute_applicant_age',string='Applicant Age')
    # period = fields.Date(string='Period')
    eligible = fields.Boolean(compute='_compute_eligibility', string='Eligible')
    2017 - 10 - 16
    def _compute_applicant_age(self):
        # self.applicant_age = date.today()-self.birth_date
        self.applicant_age = 28


    @api.depends('applicant_age')
    def _compute_eligibility(self):
        min_applicable_age = 17
        max_applicable_age = 30
        ex_service_personnel = True
        quota = True
        if quota == True:
            max_applicable_age = 32
        elif self.divisional_candiate == 'Yes':
            if self.job_id.name == 'Weather Assistant' or self.job_id.name == 'Higher Visitor':
                max_applicable_age = 35
        elif self.job_id.name == "Electrician" and ex_service_personnel == True:
            max_applicable_age = 40

        if self.applicant_age <= max_applicable_age and self.applicant_age > min_applicable_age:
            self.eligible = True
        else:
            self.eligible = False



