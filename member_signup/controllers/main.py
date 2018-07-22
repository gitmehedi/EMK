# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug
import base64

from odoo import http, _
from odoo.addons.member_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request

_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(AuthSignupHome, self).web_login(*args, **kw)
        response.qcontext.update(self.get_member_signup_config())
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        return response

    @http.route('/web/member_signup', type='http', auth='public', methods=['POST', 'GET'], website=True)
    def web_member_signup(self, *args, **kw):
        qcontext = self.get_member_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('member_signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        config = {
            'districts': self.get_districts(),
            'gender': {'male': 'Male', 'female': 'Female'},
            'occupation': self.generateDropdown('member.occupation'),
            'subject_of_interest': self.generateDropdown('member.subject.interest'),
            'hightest_certification': self.generateDropdown('member.certification'),
            'usa_work_or_study': {'yes': 'Yes', 'no': 'No'},
        }
        return request.render('member_signup.signup', {'qcontext': qcontext, 'config': config})

    def generateDropdown(self, model):
        data = []
        record = request.env[model].sudo().search([('status', '=', True)], order='id ASC')

        for rec in record:
            val = '_'.join((rec.name).strip().lower().split())
            data.append((val,rec.name))
            # data[val] = rec.name

        return data

    @http.route('/web/member_reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_member_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('member_reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return super(AuthSignupHome, self).web_login(*args, **kw)
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

    def get_member_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        IrConfigParam = request.env['ir.config_parameter']
        return {
            'member_signup_enabled': IrConfigParam.sudo().get_param('member_signup.allow_uninvited') == 'True',
            'member_reset_password_enabled': IrConfigParam.sudo().get_param('member_signup.reset_password') == 'True',
        }

    def get_member_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_member_signup_config())
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def authorized_fields(self):
        return ('login',
                'name',
                'password',
                'birthdate',
                'street',
                'street2',
                'city',
                'gender',
                'phone',
                'mobile',
                'email',
                'website',
                'occupation',
                'subject_of_interest',
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
                'image',
                'signature_image',
                'is_applicant',
                )

    def do_signup(self, values):
        # data = {
        #     'record': {},  # Values to create record
        #     'attachments': [],  # Attached files
        #     'custom': '',  # Custom fields values
        # }
        data = {}
        error_fields = []
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
            data['is_applicant'] = True
            data['membership_state'] = 'free'
            data['free_member'] = False
            data['email'] = data['login']

        assert values.values(), "The form was not properly filled in."
        # assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(values.get('token'), data)
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        if not uid:
            raise SignupError(_('Authentication Failed.'))

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
