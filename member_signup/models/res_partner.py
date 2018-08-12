# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import random, werkzeug, logging, re
from datetime import datetime, timedelta
from urlparse import urljoin

from odoo.exceptions import UserError, ValidationError, Warning
from odoo import api, fields, models, _

from odoo.addons.member_signup.models.utility import UtilityClass as utility

_logger = logging.getLogger(__name__)


class SignupError(Exception):
    pass


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))


def now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return fields.Datetime.to_string(dt)


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread', 'ir.needaction_mixin']

    member_sequence = fields.Char()

    signup_token = fields.Char(copy=False)
    signup_type = fields.Char(string='Signup Token Type', copy=False)
    signup_expiration = fields.Datetime(copy=False)
    signup_valid = fields.Boolean(compute='_compute_signup_valid', string='Signup Token is Valid')
    signup_url = fields.Char(compute='_compute_signup_url', string='Signup URL')
    birthdate = fields.Date("Birth Date")

    last_place_of_study = fields.Char(string='Last or Current Place of Study')
    place_of_study = fields.Char(string='Last or Current Place of Study')
    field_of_study = fields.Char(string='Field of Study')
    usa_work_or_study_place = fields.Char(string='Work Place')
    alumni_institute = fields.Char(string='Alumni Institute')
    current_employee = fields.Char(string='Current Employer')
    work_title = fields.Char(string='Work Title')
    work_phone = fields.Char(string='Work Phone')
    signature_image = fields.Binary(string='Signature')
    is_applicant = fields.Boolean(default=False)
    info_about_emk = fields.Text(string="How did you learn about the EMK Center?")
    application_ref = fields.Text(string="Application Ref")

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], default='male', string='Gender')
    usa_work_or_study = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no',
                                         string="Have you worked, or studied in the U.S?")
    usa_work_or_study_yes = fields.Char(string="If yes, where in the U.S have you worked, or studied?")
    subject_of_interest_others = fields.Char()

    nationality_id = fields.Many2one("res.country", "Nationality")
    occupation = fields.Many2one('member.occupation', string='Occupation')
    subject_of_interest = fields.Many2many('member.subject.interest', string='Subject of Interest')
    hightest_certification = fields.Many2one('member.certification', string='Highest Certification Achieved')

    state = fields.Selection(
        [('application', 'Application'), ('invoice', 'Invoiced'),
         ('member', 'Membership'), ('reject', 'Reject')], default='application')

    @api.model
    def _needaction_domain_get(self):
        context = self.env.context
        if context.get('menu_count') == 'application':
            return [('state', 'in', ['application'])]
        elif context.get('menu_count') == 'invoice':
            return [('state', 'in', ['invoice'])]
        elif context.get('menu_count') == 'member':
            return [('state', 'in', ['member'])]
        elif context.get('menu_count') == 'reject':
            return [('state', 'in', ['reject'])]

    @api.onchange('birthdate')
    def validate_birthdate(self):
        if self.birthdate:
            today = str(datetime.now().date())
            if self.birthdate > today:
                raise ValidationError(
                    _('Birth Date should not greater than current date.'))

    @api.constrains('birthdate')
    def _check_birthdate(self):
        today = str(datetime.now().date())
        if self.birthdate > today:
            raise ValueError(_('Birth Date should not greater than current date.'))

    @api.onchange('email')
    def validate_email(self):
        if self.email:
            utility.check_email(self.email)

    @api.constrains('email')
    def check_email(self):
        if self.email:
            utility.check_email(self.email)

    @api.model
    def create(self, vals):
        if vals:
            vals['member_sequence'] = self.env['ir.sequence'].next_by_code('res.partner.member.application')

        return super(ResPartner, self).create(vals)

    def _membership_member_states(self):
        state = super(ResPartner, self)._membership_member_states()
        return state
        return state.remove('invoiced')

    @api.multi
    def _compute_signup_valid(self):
        dt = now()
        for partner in self:
            partner.signup_valid = bool(partner.signup_token) and \
                                   (not partner.signup_expiration or dt <= partner.signup_expiration)

    @api.multi
    def _compute_signup_url(self):
        """ proxy for function field towards actual implementation """
        result = self._get_signup_url_for_action()
        for partner in self:
            partner.signup_url = result.get(partner.id, False)

    @api.multi
    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """

        res = dict.fromkeys(self.ids, False)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for partner in self:
            # when required, make sure the partner has a valid signup token
            if self.env.context.get('signup_valid') and not partner.user_ids:
                partner.signup_prepare()

            route = 'login'
            # the parameters to encode for the query
            query = dict(db=self.env.cr.dbname)
            signup_type = self.env.context.get('signup_force_type_in_url', partner.signup_type or '')
            if signup_type:
                route = 'reset_password' if signup_type == 'reset' else signup_type

            if partner.signup_token and signup_type:
                query['token'] = partner.signup_token
            elif partner.user_ids:
                query['login'] = partner.user_ids[0].login
            else:
                continue  # no signup token, no user, thus no signup url!

            fragment = dict()
            base = '/web#'
            if action == '/mail/view':
                base = '/mail/view?'
            elif action:
                fragment['action'] = action
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['res_id'] = res_id

            if fragment:
                query['redirect'] = base + werkzeug.url_encode(fragment)

            res[partner.id] = urljoin(base_url, "/web/%s?%s" % (route, werkzeug.url_encode(query)))
        return res

    @api.multi
    def action_signup_prepare(self):
        return self.signup_prepare()

    @api.model
    def _create_invoice(self):
        product_id = self.env['product.product'].search([('membership_status', '=', True)], order='id desc',
                                                        limit=1)
        if not product_id:
            raise ValidationError(_('Please configure your default Memebership Product.'))

        ins_inv = self.env['account.invoice']
        journal_id = self.env['account.journal'].search([('code', '=', 'INV')])
        account_id = self.env['account.account'].search(
            [('internal_type', '=', 'receivable'), ('deprecated', '=', False)])

        acc_invoice = {
            'partner_id': self.id,
            'date_invoice': datetime.now(),
            'user_id': self.env.user.id,
            'account_id': account_id.id,
            'state': 'draft',
            'invoice_line_ids': [
                (0, 0, {
                    'name': product_id.name,
                    'product_id': product_id.id,
                    'price_unit': product_id.list_price,
                    'account_id': journal_id.default_debit_account_id.id,
                })]
        }
        inv = ins_inv.create(acc_invoice)
        inv.action_invoice_open()

        if inv:
            self.state = 'invoice'
            pdf = self.env['report'].sudo().get_pdf([inv.id], 'account.report_invoice')
            attachment = self.env['ir.attachment'].create({
                'name': inv.number + '.pdf',
                'res_model': 'account.invoice',
                'res_id': inv.id,
                'datas_fname': inv.number + '.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf),
                'mimetype': 'application/x-pdf'
            })
            template = self.env.ref('member_signup.member_invoice_email_template')
            template.write({
                'email_cc': "nopaws_ice_iu@yahoo.com,mahtab.faisal@genweb2.com",
                'attachment_ids': [(6, 0, attachment.ids)],
            })
            user = self.env['res.users'].search([('id', '=', self.user_ids.id)])
            template.with_context({'lang': user.lang}).send_mail(user.id, force_send=True, raise_exception=True)

    @api.model
    def sendinvoice(self, inv):
        pdf = self.env['report'].get_pdf([inv.id], 'account.report_invoice')
        attachment = self.env['ir.attachment'].create({
            'name': inv.number + '.pdf',
            'res_model': 'account.invoice',
            'res_id': inv.id,
            'datas_fname': inv.number + '.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf),
            'mimetype': 'application/x-pdf'
        })
        template = self.env.ref('member_signup.member_invoice_email_template')
        template.write({
            'email_cc': "nopaws_ice_iu@yahoo.com,mahtab.faisal@genweb2.com",
            'attachment_ids': [(6, 0, attachment.ids)],
        })
        user = self.env['res.partner'].search([('id', '=', inv.partner_id.id)])
        if not user.email:
            raise ValueError(_('Configure e-mail properly.'))

        template.with_context({'lang': user.lang}).send_mail(user.id, force_send=True, raise_exception=True)

    @api.multi
    def member_invoiced(self):
        if 'application' in self.state:
            self._create_invoice()

    def mailsend(self, vals):
        template = False
        try:
            template = self.env.ref(vals['template'], raise_if_not_found=False)
        except ValueError:
            pass

        assert template._name == 'mail.template'
        obj = self.env['res.users'].search([('email', '=', vals['email'])])

        template.write({
            'email_cc': vals['email_cc'],
            'attachment_ids': vals['attachment_ids'],
        })
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        context = {
            'base_url': base_url,
        }

        for key, val in vals['context'].iteritems():
            context[key] = val

        for user in obj:
            context['lang'] = user.lang
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            template.with_context(context).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Member Application confirmation email sent for user <%s> to <%s>", user.login, user.email)

    @api.one
    def member_reject(self):
        if 'application' in self.state:
            email_cc = ''
            for gp in self.env['res.groups'].search([('name', '=', 'Manager')]):
                if gp.category_id.name == 'Membership':
                    email_cc = email_cc + ", " + gp.users.email

            vals = {
                'template': 'member_signup.member_application_rejection_email_template',
                'email': self.email,
                'email_to': self.email,
                'email_cc': email_cc,
                'attachment_ids': 'member_signup.member_application_rejection_email_template',
                'context': {},
            }
            self.mailsend(vals)
            self.state = 'reject'
            if self.user_ids.active:
                self.user_ids.active = False

    @api.multi
    def signup_cancel(self):
        return self.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})

    @api.multi
    def signup_prepare(self, signup_type="signup", expiration=False):
        """ generate a new token for the partners with the given validity, if necessary
            :param expiration: the expiration datetime of the token (string, optional)
        """
        for partner in self:
            if expiration or not partner.signup_valid:
                token = random_token()
                while self._signup_retrieve_partner(token):
                    token = random_token()
                partner.write({'signup_token': token, 'signup_type': signup_type, 'signup_expiration': expiration})
        return True

    @api.model
    def _signup_retrieve_partner(self, token, check_validity=False, raise_exception=False):
        """ find the partner corresponding to a token, and possibly check its validity
            :param token: the token to resolve
            :param check_validity: if True, also check validity
            :param raise_exception: if True, raise exception instead of returning False
            :return: partner (browse record) or False (if raise_exception is False)
        """
        partner = self.search([('signup_token', '=', token)], limit=1)
        if not partner:
            if raise_exception:
                raise SignupError("Signup token '%s' is not valid" % token)
            return False
        if check_validity and not partner.signup_valid:
            if raise_exception:
                raise SignupError("Signup token '%s' is no longer valid" % token)
            return False
        return partner

    @api.model
    def signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
        """
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        res = {'db': self.env.cr.dbname}
        if partner.signup_valid:
            res['token'] = token
            res['name'] = partner.name
        if partner.user_ids:
            res['login'] = partner.user_ids[0].login
        else:
            res['email'] = res['login'] = partner.email or ''
        return res

    @api.one
    def name_get(self):
        name = self.name
        if self.member_sequence or self.is_applicant:
            name = '[%s] %s' % (self.member_sequence, self.name)
        return (self.id, name)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        if name:
            search_name = name
            if operator != '=':
                search_name = '%s%%' % name
            member = self.search(
                ['|', ('member_sequence', operator, search_name), ('name', operator, search_name)] + args, limit=limit)
            if member.ids:
                return member.name_get()
        return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def mailcc(self):
        email_cc = ''
        for gp in self.env['res.groups'].search([('name', '=', 'Manager')]):
            if gp.category_id.name == 'Membership':
                email_cc = email_cc + ", " + gp.users.email
        return email_cc
