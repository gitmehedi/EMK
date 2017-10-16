from odoo import models, fields, api
from datetime import date,datetime, timedelta
import math


class BMDInheritedHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    applicant_age = fields.Integer(compute='_compute_applicant_age',string='Applicant Age')
    eligible = fields.Boolean(compute='_compute_eligibility', string='Eligible')

    @api.multi
    def _compute_applicant_age(self):
        for applicant in self:
            b_date = datetime.strptime(applicant.birth_date.strip(), '%Y-%m-%d')
            applicant_days = (datetime.today() - b_date).days

            applicant.applicant_age = math.floor(applicant_days/365)

        # self.applicant_age = datetime.today()-datetime.strptime(self.birth_date, "%Y-%m-%d")



    @api.multi
    @api.depends('applicant_age')
    def _compute_eligibility(self):
        for applicant in self:
            min_applicable_age = 18
            max_applicable_age = 30
            ex_service_personnel = True
            if applicant.quota:
                max_applicable_age = 32
            elif applicant.divisional_candiate == 'yes':
                if applicant.job_id.name == 'Weather Assistant' or applicant.job_id.name == 'Higher Visitor':
                    max_applicable_age = 35
            elif applicant.job_id.name == "Electrician" and ex_service_personnel == 'yes':
                max_applicable_age = 40
            if applicant.applicant_age <= max_applicable_age and applicant.applicant_age >= min_applicable_age:
                applicant.eligible = True
            else:
                applicant.eligible = False



