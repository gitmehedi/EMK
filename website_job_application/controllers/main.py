from odoo import http, _
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment


class ExtendWebsiteHrRecruitment(WebsiteHrRecruitment):
    @http.route()
    def jobs_apply(self, job, **kwargs):
        error = {}
        default = {}
        department = request.env['hr.job'].sudo().search([])
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'department': department,
        })
