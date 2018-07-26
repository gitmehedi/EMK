# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug
import base64

from odoo import http, _
from odoo.addons.member_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request

from odoo.addons.member_signup.models.utility import UtilityClass as utility

_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):

    @http.route('/web/member_reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_member_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('member_reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_application(qcontext)
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

    # @http.route(website=True, auth="public")
    # def web_login(self, redirect=None, *args, **kw):
    #     response = super(Website, self).web_login(redirect=redirect, *args, **kw)
    #     if not redirect and 'login_success' in request.params:
    #         if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
    #             redirect = '/web?' + request.httprequest.query_string
    #         else:
    #             return request.render('web.login')
    #         return http.redirect_with_hash(redirect)
    #     return response

    @http.route('/web/success', type='http', auth='public', methods=['GET'], website=True)
    def web_member_success(self, *args, **kw):

        config = {
            'name': request.params['name'],

        }

        return request.render('member_signup.success', {'config': config})

    @http.route('/web/member_signup', type='http', auth='public', methods=['POST', 'GET'], website=True)
    def web_member_signup(self, *args, **kw):
        qcontext = self.get_member_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('member_signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                auth_data = self.do_application(qcontext)

                if auth_data:
                    config = {
                        'name': auth_data['name']
                    }
                    return request.render('member_signup.success', {'name': config})


            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        package_price = request.env['product.product'].sudo().search([('membership_status', '=', True)],
                                                                     order='id desc', limit=1)

        if 'firstname' not in qcontext:
            qcontext['firstname'] = ''

        if 'state_ids' not in qcontext:
            qcontext['state_ids'] = self.generateDropdown('res.country', status=False)
        if 'per_district' in qcontext:
            qcontext['per_district'] = int(qcontext['per_district']) if qcontext['per_district'] else 0

        if 'package_price' not in qcontext:
            qcontext['package_price'] = 5000
        if 'firstname' not in qcontext:
            qcontext['state_ids'] = self.generateDropdown('res.country', status=False)
        if 'country_ids' not in qcontext:
            qcontext['country_ids'] = self.generateDropdown('res.country', status=False)
        if 'gender' not in qcontext:
            qcontext['gender'] = {'male': 'Male', 'female': 'Female'}
        if 'occupation_ids' not in qcontext:
            qcontext['occupation_ids'] = self.generateDropdown('member.occupation')
        if 'subject_of_interest_ids' not in qcontext:
            qcontext['subject_of_interest_ids'] = self.generateDropdown('member.subject.interest')
        if 'hightest_certification_ids' not in qcontext:
            qcontext['hightest_certification_ids'] = self.generateDropdown('member.certification')

        config = {
            'package_price': package_price.id,
            'state_ids': self.generateDropdown('res.country', status=False),
            'country_ids': self.generateDropdown('res.country', status=False),
            'gender': {'male': 'Male', 'female': 'Female'},
            'occupation': self.generateDropdown('member.occupation'),
            'subject_of_interest': self.generateDropdown(
                'member.subject.interest'),
            'hightest_certification': self.generateDropdown(
                'member.certification'),
            'usa_work_or_study': {
                'yes': 'Yes',
                'no': 'No'},
        }
        return request.render('member_signup.signup', qcontext)

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

    def do_application(self, values):
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
            data['name'] = data['firstname'] + ' ' + data['lastname']
            data['is_applicant'] = True
            data['membership_state'] = 'none'
            data['free_member'] = False
            data['login'] = data['email']
            data['password'] = utility.token(length=8)

        assert values.values(), "The form was not properly filled in."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        auth_data = self._signup_with_values(values.get('token'), data)
        request.env.cr.commit()
        if auth_data:
            return auth_data

    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        # uid = request.session.authenticate(db, login, password)
        # if not uid:
        #     raise SignupError(_('Authentication Failed.'))
        return {'name': values['name']}

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
            'lastname',
            'password',
            'birthdate',
            'street',
            'street2',
            'city',
            'country_id',
            'state_id',
            'city',
            'gender',
            'phone',
            'mobile',
            'email',
            'website',
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
            'image',
            'signature_image',
        )
