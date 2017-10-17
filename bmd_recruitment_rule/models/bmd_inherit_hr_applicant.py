from odoo import models, fields, api
from datetime import date,datetime, timedelta
import math


class BMDInheritedHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    applicant_age = fields.Integer(compute='_compute_applicant_age',string='Applicant Age',store=True)
    eligible = fields.Boolean(compute='_compute_eligibility', string='Eligible',store=True)

    @api.multi
    @api.depends('birth_date')
    def _compute_applicant_age(self):
        for applicant in self:
            if applicant.birth_date:
                b_date = datetime.strptime(applicant.birth_date.strip(), '%Y-%m-%d')
                if applicant.job_id.job_publish_date:
                    p_date = datetime.strptime(applicant.job_id.job_publish_date, '%Y-%m-%d')
                    applicant_age_days = (p_date - b_date).days
                else:
                    applicant_age_days = (datetime.today() - b_date).days

                applicant.applicant_age = math.floor(applicant_age_days/365)
            else:
                applicant.applicant_age=0


    @api.multi
    @api.depends('applicant_age')
    def _compute_eligibility(self):
        for applicant in self:
            min_applicable_age = 18
            max_applicable_age = 30
            if applicant.quota:
                max_applicable_age = 32
            elif applicant.divisional_candiate == 'yes':
                if applicant.job_id.name == 'Weather Assistant' or applicant.job_id.name == 'Higher Visitor':
                    max_applicable_age = 35
            elif applicant.job_id.name == "Electrician" and applicant.ex_service_personnel == 'yes':
                max_applicable_age = 40

            if applicant.applicant_age >= min_applicable_age and applicant.applicant_age <= max_applicable_age:
                applicant.eligible = True
            else:
                applicant.eligible = False



