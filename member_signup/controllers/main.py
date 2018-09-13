# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging, werkzeug, base64, json
import cStringIO
import json
import logging
import werkzeug.wrappers
from PIL import Image, ImageFont, ImageDraw

from odoo import http, tools, _
from odoo.addons.member_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request, Response

from odoo.addons.opa_utility.models.utility import Utility as utility

_logger = logging.getLogger(__name__)


class MemberApplicationContoller(Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(MemberApplicationContoller, self).web_login(*args, **kw)
        response.qcontext.update(self.get_auth_signup_config())
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        return response

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        IrConfigParam = request.env['ir.config_parameter']
        return {
            'member_signup_enabled': IrConfigParam.sudo().get_param('member_signup.allow_uninvited') == 'True',
            'member_reset_password_enabled': IrConfigParam.sudo().get_param('member_signup.reset_password') == 'True',
        }

    @http.route('/web/member_reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_signup_context()

        if not qcontext.get('token') and not qcontext.get('member_reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.create_applicant(qcontext)
                    return super(MemberApplicationContoller, self).web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception, e:
                qcontext['error'] = e.message or e.name

        return request.render('member_signup.reset_password', qcontext)

    def get_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""
        IrConfigParam = request.env['ir.config_parameter']
        return {
            'member_signup_enabled': IrConfigParam.sudo().get_param('member_signup.allow_uninvited') == 'True',
            'member_reset_password_enabled': IrConfigParam.sudo().get_param('member_signup.reset_password') == 'True',
        }

    @http.route('/page/checkemail', auth='public', type='http', methods=['POST', 'GET'], csft=False)
    def email_check(self, **post):
        response = {'response': 'Invalid Request'}
        if request.httprequest.method == 'GET' and 'email' in request.params:
            email = request.params.get('email')
            response = {'email': 0}
            record = request.env['res.users'].sudo().search([('login', '=', email)])
            if len(record) > 0:
                response['email'] = 1
        return json.dumps(response)

    @http.route('/page/application', type='http', auth='public', methods=['POST', 'GET'], website=True)
    def signup(self, *args, **kw):
        qcontext = self.get_signup_context()
        package_price = request.env['product.product'].sudo().search([('membership_status', '=', True)],
                                                                     order='id desc', limit=1)
        qcontext['package_price'] = "{0:.2f}".format(package_price.list_price) if package_price else 0

        if not qcontext.get('token') and not qcontext.get('member_signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if request.httprequest.method == 'POST':
            try:
                auth_data = self.create_applicant(qcontext)
                if auth_data:
                    res_obj = request.env['res.partner'].sudo()
                    recipient_email = res_obj.groupmail({'group': ['Officer'], 'category': 'Membership'})
                    vals = {
                        'template': 'member_signup.member_application_email_template',
                        'email_to': auth_data['email'],
                        'context': auth_data,
                    }

                    officer = {
                        'template': 'member_signup.mem_app_email_to_officer_tmpl',
                        'email_to': recipient_email,
                        'context': auth_data,
                    }
                    res_obj.mailsend(vals)
                    res_obj.mailsend(officer)
                    return request.render('member_signup.success', {'name': auth_data['name']})
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("email"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        qcontext['firstname'] = None if 'firstname' not in qcontext else qcontext['firstname']
        qcontext['lastname2'] = None if 'lastname2' not in qcontext else qcontext['lastname2']
        qcontext['lastname'] = None if 'lastname' not in qcontext else qcontext['lastname']
        qcontext['phone'] = None if 'phone' not in qcontext else qcontext['phone']
        qcontext['mobile'] = None if 'mobile' not in qcontext else qcontext['mobile']
        qcontext['weburl'] = None if 'weburl' not in qcontext else qcontext['weburl']
        qcontext['zipcode'] = None if 'zipcode' not in qcontext else qcontext['zipcode']

        qcontext['last_place_of_study'] = None if 'last_place_of_study' not in qcontext else qcontext[
            'last_place_of_study']
        qcontext['field_of_study'] = None if 'field_of_study' not in qcontext else qcontext['field_of_study']
        qcontext['place_of_study'] = None if 'place_of_study' not in qcontext else qcontext['place_of_study']
        qcontext['alumni_institute'] = None if 'alumni_institute' not in qcontext else qcontext['alumni_institute']
        qcontext['current_employee'] = None if 'current_employee' not in qcontext else qcontext['current_employee']
        qcontext['work_title'] = None if 'work_title' not in qcontext else qcontext['work_title']
        qcontext['work_phone'] = None if 'work_phone' not in qcontext else qcontext['work_phone']
        qcontext['info_about_emk'] = None if 'info_about_emk' not in qcontext else qcontext['info_about_emk']
        qcontext['usa_work_or_study'] = 'no' if 'usa_work_or_study' not in qcontext else qcontext[
            'usa_work_or_study']
        qcontext['gender'] = 'male' if 'gender' not in qcontext else qcontext['gender']
        qcontext['country_id'] = int(qcontext['country_id']) if 'country_id' in qcontext else 20

        if 'per_district' in qcontext:
            qcontext['per_district'] = int(qcontext['per_district']) if qcontext['per_district'] else ''
        if 'occupation' in qcontext:
            qcontext['occupation'] = int(qcontext['occupation']) if qcontext['occupation'] else ''

        if 'hightest_certification' in qcontext:
            qcontext['hightest_certification'] = int(qcontext['hightest_certification']) if qcontext[
                'hightest_certification'] else ''

        if 'subject_of_interest' not in qcontext:
            qcontext['subject_of_interest'] = []
        else:
            qcontext['subject_of_interest'] = [int(val) for val in
                                               request.httprequest.form.getlist('subject_of_interest')]
        if 'country_ids' not in qcontext:
            qcontext['country_ids'] = self.generateDropdown('res.country', status=False)

        if 'occupation_ids' not in qcontext:
            qcontext['occupation_ids'] = self.generateDropdown('member.occupation')

        if 'subject_of_interest_ids' not in qcontext:
            qcontext['subject_of_interest_ids'] = self.generateDropdown('member.subject.interest')

        if 'hightest_certification_ids' not in qcontext:
            qcontext['hightest_certification_ids'] = self.generateDropdown('member.certification')

        if 'usa_work_or_study_ids' not in qcontext:
            qcontext['usa_work_or_study_ids'] = {'yes': 'Yes', 'no': 'No'}
        if 'gender_ids' not in qcontext:
            qcontext['gender_ids'] = {'male': 'Male', 'female': 'Female'}

        return request.render('member_signup.signup', qcontext)

    def get_signup_context(self):
        qcontext = request.params.copy()
        qcontext.update(self.get_signup_config())
        qcontext['baseurl'] = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if qcontext.get('token'):
            try:
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def create_applicant(self, values):
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
            data['name'] = data['firstname'] + ' ' + data['lastname'] + ' ' + data['lastname2']
            data['is_applicant'] = True
            data['membership_state'] = 'none'
            data['free_member'] = False
            data['login'] = data['email']
            data['website'] = data['weburl']
            data['zip'] = data['zipcode']
            vals = [int(val) for val in request.httprequest.form.getlist('subject_of_interest')]
            data['subject_of_interest'] = [(6, 0, vals)]
            data['password'] = utility.token(length=8)
        # self.upload_attachment(request.httprequest.files.getlist('attachment'))
        assert values.values(), "The form was not properly filled in."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang

        db, login, password = request.env['res.users'].sudo().signup(data, values.get('token'))
        if login:
            res_id = request.env['res.users'].sudo().search([('email', '=', login)])
            groups = request.env['res.groups'].sudo().search(
                [('name', '=', 'Applicants'), ('category_id.name', '=', 'Membership')])
            groups.write({'users': [(6, 0, [res_id.id])]})
            files = request.httprequest.files.getlist('attachment')
            self.upload_attachment(files, res_id.partner_id.id)

        request.env.cr.commit()
        return {'name': data['name'],
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
        status = [('status', '=', True)] if status else []
        record = request.env[model].sudo().search(status, order='id ASC')
        for rec in record:
            if status:
                val = '_'.join((rec.name).strip().lower().split())
                data.append((val, rec.name))
            else:
                data.append((rec.id, rec.name))
        return data

    def authorized_fields(self):
        return (
            'firstname',
            'lastname2',
            'lastname',
            'password',
            'birthdate',
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
            'subject_of_interest',
            'subject_of_interest_others',
            'last_place_of_study',
            'hightest_certification',
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
