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
                auth_data = self.apply_for_job(context,job)
                if auth_data:
                    mail_ins = request.env['res.partner'].sudo()
                    mail_applicant = {
                        'template': 'website_job_application.applicant_email_confirm_template',
                        'email_to': auth_data['email_from'],
                        'context': auth_data,
                    }

                    try:
                        mail_ins.mailsend(mail_applicant)

                        return request.render('website_hr_recruitment.success', {'firstname': auth_data['firstname']})
                    except Exception, e:
                        print(e)
                        return request.render('website_hr_recruitment.success', {'firstname': auth_data['firstname']})
                # return request.render('website_hr_recruitment.success', {'firstname': auth_data['firstname']})

            except (ExtendWebsiteHrRecruitment, AssertionError) as e:
                context['error'] = _("Could not create a new account.")
        else:
            context = self.validate_form_data(context)

        return request.render('website_hr_recruitment.apply', context)

    def validate_form_data(self, qcontext):

        qcontext['firstname'] = None if 'firstname' not in qcontext else qcontext['firstname']
        qcontext['partner_last_name'] = None if 'partner_last_name' not in qcontext else qcontext['partner_last_name']
        qcontext['father_name'] = None if 'father_name' not in qcontext else qcontext['father_name']
        qcontext['mother_name'] = None if 'mother_name' not in qcontext else qcontext['mother_name']
        qcontext['birth_date'] = None if 'birth_date' not in qcontext else qcontext['birth_date']

        qcontext['partner_phone'] = None if 'partner_phone' not in qcontext else qcontext['partner_phone']
        qcontext['email_from'] = None if 'email_from' not in qcontext else qcontext['email_from']
        qcontext['nationality'] = None if 'nationality' not in qcontext else qcontext['nationality']
        qcontext['gender'] = None if 'gender' not in qcontext else qcontext['gender']

        qcontext['pre_address_1'] = None if 'pre_address_1' not in qcontext else qcontext['pre_address_1']
        qcontext['pre_address_2'] = None if 'pre_address_2' not in qcontext else qcontext['pre_address_2']
        qcontext['pre_zip_postal'] = None if 'pre_zip_postal' not in qcontext else qcontext['pre_zip_postal']
        qcontext['pre_country_id'] = int(qcontext['pre_country_id']) if 'pre_country_id' in qcontext else 20

        qcontext['per_address_1'] = None if 'per_address_1' not in qcontext else qcontext['per_address_1']
        qcontext['per_address_2'] = None if 'per_address_2' not in qcontext else qcontext['per_address_2']
        qcontext['per_zip_postal'] = None if 'per_zip_postal' not in qcontext else qcontext['per_zip_postal']
        qcontext['per_country_id'] = int(qcontext['per_country_id']) if 'per_country_id' in qcontext else 20

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

    def apply_for_job(self, values,job):
        data, error_fields = {}, []
        authorized_fields = self.authorized_fields()

        """ Shared helper that creates a res.partner out of a token """
        values = {key: values.get(key) for key in authorized_fields}
        for field_name, field_value in values.items():
            if hasattr(field_value, 'filename'):
                field_name = field_name.rsplit('[', 1)[0]
                field_value.field_name = field_name
                data[field_name] = base64.encodestring(field_value.read())
            elif field_name in authorized_fields:
                try:
                    data[field_name] = field_value
                except ValueError:
                    error_fields.append(field_name)

        data['name'] = '%s\'s Application' % data['firstname']
        data['partner_name'] = data['firstname'] + ' ' + data['partner_last_name']
        # data['partner_mobile'] = data['partner_mobile']
        data['job_id'] = job.id
        data['job_name'] = job.name
        print(data['job_name'])
        applicant = request.env['hr.applicant'].sudo().post_applicant_data(data, values.get('token'))

        files = request.httprequest.files.getlist('Resume')
        self.upload_attachment(files, applicant.id)
        return data

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
                'res_model': 'hr.applicant',
                'res_id': id,
                'datas': base64.b64encode(attachment),
            })

    def get_signup_context(self):
        qctx = request.params.copy()
        qctx['baseurl'] = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return qctx

    def authorized_fields(self):
        return (
            'id',
            'name',
            'firstname',
            'father_name',
            'mother_name',
            'partner_last_name',
            'birth_date',
            'gender',
            'nationality',
            'pre_address_1',
            'pre_address_2',
            'pre_zip_postal',
            'pre_country_id',
            'per_address_1',
            'per_address_2',
            'per_zip_postal',
            'per_country_id',
            # 'partner_phone',
            'partner_mobile',
            'email_from',
            'job_id',
            'partner_name',
            'applicant_image',

        )

