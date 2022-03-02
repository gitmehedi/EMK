import base64

from odoo import http, _
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.http import request


class ExtendWebsiteHrRecruitment(WebsiteHrRecruitment):
    @http.route('/jobs/apply/<model("hr.job"):job>', type='http', auth="public", method=['GET', 'POST'], website=True)
    def jobs_apply(self, job, **kwargs):
        context = self.get_signup_context()

        if request.httprequest.method == 'POST' and ('error' not in context):
            try:
                auth_data = self.apply_for_job(context)
            except (ExtendWebsiteHrRecruitment, AssertionError) as e:
                context['error'] = _("Could not create a new account.")
        else:
            context = self.validate_form_data(context)

        # return request.render('member_signup.signup', qcontext)

        # error = {}
        # default = {}
        # districts = sorted(self.get_districts())
        # # authorize_districts = request.env['bd.district'].sudo().browse(job.authorize_district.ids)
        # # authorize_districts = request.env['bd.district'].sudo().search([])
        # # degree = request.env['hr.recruitment.degree'].sudo().search([])
        # gender = self.generateGender()
        # # quota = self.get_quota()
        # religion = self.get_religion()
        # department = request.env['hr.job'].sudo().search([])
        # if 'website_hr_recruitment_error' in request.session:
        #     error = request.session.pop('website_hr_recruitment_error')
        #     default = request.session.pop('website_hr_recruitment_default')
        return request.render("website_hr_recruitment.apply", context)
        # {
        #     'job': job,
        #     'error': error,
        #     'default': default,
        #     'department': department,
        #     'districts': districts,
        #     # 'quota': quota,
        #     'religion': religion,
        #     # 'authorize_districts': authorize_districts,
        #     # 'degree': degree,
        #     'gender': gender,
        #
        # })

    def validate_form_data(self, qcontext):
        qcontext['partner_name'] = None if 'partner_name' not in qcontext else qcontext['partner_name']
        qcontext['partner_last_name'] = None if 'partner_last_name' not in qcontext else qcontext['partner_last_name']
        qcontext['father_name'] = None if 'father_name' not in qcontext else qcontext['father_name']
        qcontext['mother_name'] = None if 'mother_name' not in qcontext else qcontext['mother_name']
        qcontext['partner_last_name'] = None if 'partner_last_name' not in qcontext else qcontext['partner_last_name']
        qcontext['partner_last_name'] = None if 'partner_last_name' not in qcontext else qcontext['partner_last_name']

        qcontext['partner_phone'] = None if 'partner_phone' not in qcontext else qcontext['partner_phone']
        qcontext['email_from'] = None if 'email_from' not in qcontext else qcontext['email_from']
        qcontext['nationality'] = None if 'weburl' not in qcontext else qcontext['nationality']
        qcontext['gender'] = None if 'gender' not in qcontext else qcontext['gender']

        qcontext['pre_address_1'] = None if 'pre_address_1' not in qcontext else qcontext['pre_address_1']
        qcontext['pre_address_2'] = None if 'pre_address_2' not in qcontext else qcontext['pre_address_2']
        qcontext['pre_zip_postal'] = None if 'pre_zip_postal' not in qcontext else qcontext['pre_zip_postal']
        qcontext['pre_district'] = None if 'pre_district' not in qcontext else qcontext['pre_district']
        qcontext['pre_country_id'] = int(qcontext['pre_country_id']) if 'pre_country_id' in qcontext else 20

        qcontext['per_address_1'] = None if 'per_address_1' not in qcontext else qcontext['per_address_1']
        qcontext['per_address_2'] = None if 'per_address_2' not in qcontext else qcontext['per_address_2']
        qcontext['per_zip_postal'] = None if 'per_zip_postal' not in qcontext else qcontext['per_zip_postal']
        qcontext['per_district'] = None if 'pre_district' not in qcontext else qcontext['pre_district']
        qcontext['per_country_id'] = int(qcontext['per_country_id']) if 'per_country_id' in qcontext else 20

        if 'per_district' in qcontext:
            qcontext['per_district'] = int(qcontext['per_district']) if qcontext['per_district'] else ''

        if 'gender' in qcontext:
            qcontext['gender'] = int(qcontext['gender']) if qcontext['gender'] else ''

        if 'country_ids' not in qcontext:
            qcontext['country_ids'] = self.generateDropdown('res.country', status=False)

        if 'gender_ids' not in qcontext:
            qcontext['gender_ids'] = self.generateDropdown('res.gender')

        return qcontext

    def generateDropdown(self, model, status=False):
        data = []
        status = [('status', '=', True)] if status else []
        record = request.env[model].sudo().search(status, order='id ASC')
        for rec in record:
            if status:
                val = '_'.join((rec.name).strip().lower().split())
                data.append((val, rec.name))
            else:
                data.append((rec.id, rec.name))
        return data

    def apply_for_job(self, values):
        data, error_fields = {}, []
        authorized_fields = self.authorized_fields()

        """ Shared helper that creates a res.partner out of a token """
        # values = {key: values.get(key) for key in authorized_fields}
        for field_name, field_value in values.items():
            if hasattr(field_value, 'filename'):
                field_name = field_name.rsplit('[', 1)[0]
                field_value.field_name = field_name
                data[field_name] = base64.encodestring(field_value.read())
            elif field_name in authorized_fields:
                try:
                    # input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    # data['record'][field_name] = input_filter(self, field_name, field_value)
                    data[field_name] = field_value
                except ValueError:
                    error_fields.append(field_name)

        if len(data) > 0:
            fullname = data['firstname'] + ' ' + data['middlename'] + ' ' + data['lastname']
            data['name'] = ' '
            data['is_applicant'] = True
            data['membership_state'] = 'none'
            data['free_member'] = False
            data['login'] = data['email']
            data['website'] = data['weburl']
            data['zip'] = data['zipcode']
            vals = [int(val) for val in request.httprequest.form.getlist('subject_of_interest')]
            data['subject_of_interest'] = [(6, 0, vals)]
            data['usa_work_or_study'] = data['usa_work_or_study'].lower()
            # data['password'] = Utility.token(length=8)
        # self.upload_attachment(request.httprequest.files.getlist('attachment'))
        assert values.values(), "The form was not properly filled in."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang

        db, login, password = request.env['res.users'].sudo().signup(data, values.get('token'))
        if login:
            groups = {
                'grp_name': 'Applicants',
                'cat_name': 'Membership',
            }
            res_id = request.env['res.users'].sudo().create_temp_user(login, groups)
            files = request.httprequest.files.getlist('attachment')
            self.upload_attachment(files, res_id.partner_id.id)

        request.env.cr.commit()
        return {'name': fullname,
                'email': login,
                'password': password,
                'res_id': res_id.id,
                'member_seq': res_id.partner_id.member_sequence}

    def upload_attachment(self, files, id):
        Attachments = request.env['ir.attachment']
        for file in files:
            name = file.filename
            attachment = file.read()
            Attachments.sudo().create({
                'name': name,
                'datas_fname': name,
                'res_name': name,
                'type': 'binary',
                'res_model': 'res.partner',
                'res_id': id,
                'datas': base64.b64encode(attachment),
            })

    def generateDropdown(self, model, status=False):
        data = []
        status = [('active', '=', True), ('pending', '=', False)] if status else []
        record = request.env[model].sudo().search(status, order='id ASC')
        for rec in record:
            if status:
                val = '_'.join((rec.name).strip().lower().split())
                data.append((val, rec.name))
            else:
                data.append((rec.id, rec.name))
        return data

    def get_signup_context(self):
        qcontext = request.params.copy()
        qcontext['baseurl'] = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # if qcontext.get('token'):
        #     try:
        #         token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
        #         for k, v in token_infos.items():
        #             qcontext.setdefault(k, v)
        #     except:
        #         qcontext['error'] = _("Invalid signup token")
        #         qcontext['invalid_token'] = True
        return qcontext

    def authorized_fields(self):
        return (
            'firstname',
            'middlename',
            'lastname',
            'password',
            'birth_date',
            'street',
            'street2',
            'city',
            'zipcode',
            'country_id',
            'gender',
            'phone',
            'mobile',
            'email',
            'weburl',
            'occupation',
            'occupation_other',
            'subject_of_interest',
            'subject_of_interest_others',
            'last_place_of_study',
            'highest_certification',
            'highest_certification_other',
            'field_of_study',
            'place_of_study',
            'usa_work_or_study',
            'usa_work_or_study_place',
            'alumni_institute',
            'current_employee',
            'work_title',
            'work_phone',
            'info_about_emk',
            'image',
            'signature_image',
        )

