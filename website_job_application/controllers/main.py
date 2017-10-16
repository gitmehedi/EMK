from odoo import http, _
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment


class ExtendWebsiteHrRecruitment(WebsiteHrRecruitment):
    @http.route()
    def jobs_apply(self, job, **kwargs):
        error = {}
        default = {}
        districts = self.get_districts()
        authorize_districts = request.env['job.district'].sudo().browse(job.authorize_district.ids)

        quota = self.get_quota()
        religion = self.get_religion()
        department = request.env['hr.job'].sudo().search([])
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'department': department,
            'districts': districts,
            'quota': quota,
            'religion': religion,
            'authorize_districts': authorize_districts,
        })

    def get_religion(self):
        return {
            '': '---Please Select---',
            'islam': 'Islam',
            'hinduism': 'Hinduism',
            'christianity': 'Christianity',
            'buddhism': 'Buddhism',
            'others': 'Others'
        }

    def get_quota(self):
        return {
            "": "---Please Select---",
            "freedom_fighter": "Son-daughter/Grandson-Granddaughter of Freedom Fighters/Martyred Freedom Fighters",
            "ansar_and_vdp_member": "Ansar and VDP Member",
            "indigenous_community": "Indigenous Community",
            "others": "Others",
        }

    def get_districts(self):
        return {
            '': "---Please Select---",
            'Barguna': "Barguna",
            'Barisal': "Barisal",
            'Bhola': "Bhola",
            'Jhalokati': "Jhalokati",
            'Patuakhali': "Patuakhali",
            'Pirojpur': "Pirojpur",
            'Bandarban': "Bandarban",
            'Brahmanbaria': "Brahmanbaria",
            'Chandpur': "Chandpur",
            'Chittagong': "Chittagong",
            'Comilla': "Comilla",
            'Feni': "Feni",
            'Khagrachhari': "Khagrachhari",
            'Lakshmipur': "Lakshmipur",
            'Noakhali': "Noakhali",
            'Rangamati': "Rangamati",
            'Dhaka': "Dhaka",
            'Faridpur': "Faridpur",
            'Gazipur': "Gazipur",
            'Gopalganj': "Gopalganj",
            'Jamalpur': "Jamalpur",
            'Kishoreganj': "Kishoreganj",
            'Madaripur': "Madaripur",
            'Manikganj': "Manikganj",
            'Munshiganj': "Munshiganj",
            'Mymensingh': "Mymensingh",
            'Narayanganj': "Narayanganj",
            'Narsingdi': "Narsingdi",
            'Netrakona': "Netrakona",
            'Rajbari': "Rajbari",
            'Shariatpur': "Shariatpur",
            'Sherpur': "Sherpur",
            'Tangail': "Tangail",
            'Bagerhat': "Bagerhat",
            'Chuadanga': "Chuadanga",
            'Jessore': "Jessore",
            'Jhenaidah': "Jhenaidah",
            'Khulna': "Khulna",
            'Kushtia': "Kushtia",
            'Magura': "Magura",
            'Meherpur': "Meherpur",
            'Narail': "Narail",
            'Satkhira': "Satkhira",
            'Bogra': "Bogra",
            'Joypurhat': "Joypurhat",
            'Naogaon': "Naogaon",
            'Natore': "Natore",
            'Nawabganj': "Nawabganj",
            'Pabna': "Pabna",
            'Rajshahi': "Rajshahi",
            'Sirajganj': "Sirajganj",
            'Dinajpur': "Dinajpur",
            'Gaibandha': "Gaibandha",
            'Kurigram': "Kurigram",
            'Lalmonirhat': "Lalmonirhat",
            'Nilphamari': "Nilphamari",
            'Panchagarh': "Panchagarh",
            'Rangpur': "Rangpur",
            'Thakurgaon': "Thakurgaon",
            'Habiganj': "Habiganj",
            'Moulvibazar': "Moulvibazar",
            'Sunamganj': "Sunamganj",
            'Sylhet': "Sylhet",
        }
