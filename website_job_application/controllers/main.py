from odoo import http, _
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment


class ExtendWebsiteHrRecruitment(WebsiteHrRecruitment):
    @http.route()
    def jobs_apply(self, job, **kwargs):
        error = {}
        default = {}
        districts = sorted(self.get_districts())
        # authorize_districts = request.env['bd.district'].sudo().browse(job.authorize_district.ids)
        # authorize_districts = request.env['bd.district'].sudo().search([])
        # degree = request.env['hr.recruitment.degree'].sudo().search([])
        gender = self.generateGender()
        # quota = self.get_quota()
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
            # 'quota': quota,
            'religion': religion,
            # 'authorize_districts': authorize_districts,
            # 'degree': degree,
            'gender': gender,


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
            "no_quota": "No Quota",
            "freedom_fighter": "Son-daughter/Grandson-Granddaughter of Freedom Fighters/Martyred Freedom Fighters",
            "ansar_and_vdp_member": "Ansar and VDP Member",
            "indigenous_community": "Indigenous Community",
            "others": "Others",
        }
    def generateGender(self, status=False):
        data = []
        status = [('active', '=', True),('pending', '=', False)] if status else []
        record = request.env['res.gender'].sudo().search(status, order='id ASC')
        for rec in record:
            if status:
                val = '_'.join((rec.name).strip().lower().split())
                data.append((val, rec.name))
            else:
                data.append((rec.id, rec.name))
        return data

    def get_districts(self):
        return {
            'Bagerhat': "Bagerhat",
            'Bandarban': "Bandarban",
            'Barguna': "Barguna",
            'Barisal': "Barisal",
            'Bhola ': "Bhola ",
            'Bogra': "Bogra",
            'Brahmanbaria': "Brahmanbaria",
            'Chandpur': "Chandpur",
            'Chittagong': "Chittagong",
            'Chuadanga': "Chuadanga",
            'Comilla': "Comilla",
            'Cox\'sBazar': "Cox\'s Bazar",
            'Dhaka': "Dhaka",
            'Dinajpur': "Dinajpur",
            'Faridpur': "Faridpur",
            'Feni': "Feni",
            'Gaibandha': "Gaibandha",
            'Gazipur': "Gazipur",
            'Gopalganj': "Gopalganj",
            'Habiganj': "Habiganj",
            'Jamalpur': "Jamalpur",
            'Jessore': "Jessore",
            'Jhalokati': "Jhalokati",
            'Jhenaidah': "Jhenaidah",
            'Joypurhat': "Joypurhat",
            'Khagrachhari': "Khagrachhari",
            'Khulna': "Khulna",
            'Kishoreganj': "Kishoreganj",
            'Kurigram': "Kurigram",
            'Kushtia': "Kushtia",
            'Lakshmipur': "Lakshmipur",
            'Lalmonirhat': "Lalmonirhat",
            'Madaripur': "Madaripur",
            'Magura': "Magura",
            'Manikganj': "Manikganj",
            'Meherpur': "Meherpur",
            'Moulvibazar': "Moulvibazar",
            'Munshiganj': "Munshiganj",
            'Mymensingh': "Mymensingh",
            'Naogaon': "Naogaon",
            'Narail': "Narail",
            'Narayanganj': "Narayanganj",
            'Narsingdi': "Narsingdi",
            'Natore': "Natore",
            'Nawabganj': "Nawabganj",
            'Netrakona': "Netrakona",
            'Nilphamari': "Nilphamari",
            'Noakhali': "Noakhali",
            'Pabna': "Pabna",
            'Panchagarh': "Panchagarh",
            'Patuakhali': "Patuakhali",
            'Pirojpur': "Pirojpur",
            'Rajbari': "Rajbari",
            'Rajshahi': "Rajshahi",
            'Rangamati': "Rangamati",
            'Rangpur': "Rangpur",
            'Satkhira': "Satkhira",
            'Shariatpur': "Shariatpur",
            'Sherpur': "Sherpur",
            'Sirajganj': "Sirajganj",
            'Sunamganj': "Sunamganj",
            'Sylhet': "Sylhet",
            'Tangail': "Tangail",
            'Thakurgaon': "Thakurgaon",

        }

    # def authorized_fields(self):
    #     return (
    #         'id',
    #         'department',
    #         'religion',
    #         'gender'
    #     )