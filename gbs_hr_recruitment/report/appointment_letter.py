from odoo import api, fields, models

class GetAppointLetter(models.AbstractModel):
    _name='report.gbs_hr_recruitment.report_app_letter'

    @api.model
    def render_html(self,docids,data=None):

        applicant_pool=self.env['hr.applicant'].search([('id','=',data['applicant_id'])])

        amt_to_word = self.env['res.currency'].amount_to_word(float(applicant_pool.salary_proposed))

        docargs = {
            'applicant_name':applicant_pool.partner_name,
            'job_id':applicant_pool.job_id,
            'department_id':applicant_pool.department_id,
            'salary_proposed':float(applicant_pool.salary_proposed),
            'amount_to_text_bdt':amt_to_word,
            'availability':applicant_pool.availability,
            'manager_id':applicant_pool.manager_id,
            'company_id':applicant_pool.company_id,

        }
        return self.env['report'].render('gbs_hr_recruitment.report_app_letter', docargs)


        # class GetAppointLetter(models.AbstractModel):
        #     _name='report.gbs_hr_recruitment.report_letter'
        #
        #     @api.model
        #     def render_html(self,docids,data=None):
        #
        #
        #         docargs = {
        #
        #
        #         }
        #         return self.env['report'].render('gbs_hr_recruitment.report_letter', docargs)