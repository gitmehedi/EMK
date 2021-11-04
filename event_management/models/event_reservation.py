# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventReservation(models.Model):
    _name = 'event.reservation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'poc_id'
    _order = 'id desc'
    _description = 'Event Reservation'

    def get_employee(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        return employee

    name = fields.Char(string='ID', readonly=True, states={'draft': [('readonly', False)]})
    event_name = fields.Char(string='Event Name',   readonly=True, states={'draft': [('readonly', False)]})
    poc_id = fields.Many2one('res.partner',   string='PoC Name', domain=[('is_poc', '=', True)],
                             readonly=True, track_visibility='onchange',
                             states={'draft': [('readonly', False), ('required', False)]})
    contact_number = fields.Char(string="Contact Number", readonly=True, related='poc_id.mobile')
    work_email = fields.Char(string="Email", readonly=True, related='poc_id.email')
    org_id = fields.Many2one('hr.employee', string='Organizer Name', default=get_employee,
                               track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False), ('required', False)]})
    event_type_id = fields.Many2one('event.type', string='Event Type',   track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    event_id = fields.Many2one('event.event', string='Event', track_visibility='onchange', readonly=True)
    poc_type_id = fields.Many2one('event.poc.type', string="PoC Type",
                                  track_visibility='onchange',
                                  readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    pillar_id = fields.Many2one('event.pillar', string='Event Pillar', track_visibility='onchange', readonly=True,
                                states={'draft': [('readonly', False), ('required', False)]})
    theme_id = fields.Many2one('event.theme', string='Event Theme', track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    facilities_ids = fields.Many2many('event.task.type', string="Facilities Requested", track_visibility='onchange',
                                        readonly=True,
                                      states={'draft': [('readonly', False), ('required', False)]})
    attendee_number = fields.Integer('No. of Attendees',   track_visibility='onchange',
                                     readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    total_session = fields.Integer('No. of Sessions',   track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    start_date = fields.Datetime(string='Start Date',   track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    end_date = fields.Datetime(string='End Date',   track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    last_date_reg = fields.Datetime(string='Last Date of Registration',   track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    request_date = fields.Datetime(string='Requested Date',   track_visibility='onchange',
                                   default=fields.Datetime.now,
                                   readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    description = fields.Html('Description', track_visibility='onchange',   sanitize=False,
                              readonly=True, states={'draft': [('readonly', False), ('required', False)]})

    payment_type = fields.Selection([('paid', 'Paid'), ('free', 'Free')],   default='paid', string='Type',
                                    readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    mode_of_payment = fields.Selection([('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'bKash')],
                                       default='cash', string='Mode of Payment', track_visibility='onchange',
                                       readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    paid_amount = fields.Float(string='Paid Amount', digits=(12, 2), track_visibility='onchange',
                               states={'draft': [('readonly', False), ('required', False)]})
    refundable_amount = fields.Float(string='Refundable Amount', digits=(12, 2), track_visibility='onchange',
                                     readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    approved_budget = fields.Float(string='Approved Budget', digits=(12, 2), track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    proposed_budget = fields.Float(string='Proposed Budget', digits=(12, 2), track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    rules_regulation = fields.Html(string='Rules and Regulation', track_visibility='onchange', sanitize=True,
                                   readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    date_of_payment = fields.Date(string="Date for Payment", track_visibility='onchange',
                                  readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    notes = fields.Html(string="Comments/Notes", track_visibility='onchange', sanitize=False,
                        readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    purpose_of_event = fields.Html(string="Purpose of Event", track_visibility='onchange', sanitize=False,
                                   readonly=True, states={'draft': [('readonly', False), ('required', False)]})
    target_audience_group = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                             string="Target Audience Group", readonly=True,
                                             states={'draft': [('readonly', False), ('required', False)]})
    target_age = fields.Integer(string="Target Age",   readonly=True,
                                states={'draft': [('readonly', False), ('required', False)]})
    outreach_plan = fields.Selection([('social_media', 'Social Media Promotions'),
                                      ('press_coverage', 'Press Coverage'),
                                      ('designing', 'Designing'),
                                      ('others', 'Others'),
                                      ], string="Outreach Plan",  readonly=True,
                                     states={'draft': [('readonly', False), ('required', False)]})
    outreach_plan_other = fields.Char(string="Outreach Plan Other", readonly=True,
                                      states={'draft': [('readonly', False), ('required', False)]})
    snacks_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                       string="Food/Beverage/Snacks?", readonly=True,
                                       states={'draft': [('readonly', False), ('required', False)]})
    paid_attendee = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                     string="Participation Charge", readonly=True,
                                     states={'draft': [('readonly', False), ('required', False)]})
    participating_amount = fields.Float(string="Participation Amount", readonly=True,
                                        states={'draft': [('readonly', False), ('required', False)]})
    space_id = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string="Need EMK Space?",
                                readonly=True,  states={'draft': [('readonly', False), ('required', False)]})
    seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')],
                                          readonly=True, string='Available Seats', default="limited",
                                          states={'draft': [('readonly', False), ('required', False)]})
    image_medium = fields.Binary(string='Photo', attachment=True, readonly=True,
                                 states={'draft': [('readonly', False), ('required', False)]})

    state = fields.Selection(
        [('draft', 'Draft'), ('reservation', 'Reservation'), ('on_process', 'On Process'),
         ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], string="State", default="draft",
        track_visibility='onchange')

    @api.constrains('start_date', 'end_date')
    def _check_start_date(self):
        if self.start_date:
            dt_now = fields.datetime.now()
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)
            if start_date < dt_now:
                raise ValidationError(_("Event start date cannot be past date from current date."))
            if self.start_date > self.end_date:
                raise ValidationError(_("Event end date must greater than event end date."))
        if self.end_date and not self.start_date:
            self.end_date = ''

    # @api.constrains('event_name')
    # def _check_name(self):
    #     name = self.search([('event_name', '=ilike', self.event_name)])
    #     if len(name) > 1:
    #         raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    # @api.constrains('payment_type', 'paid_amount', 'refundable_amount')
    # def _check_payment(self):
    #
    #     if self.payment_type == 'paid' and self.state=='draft':
    #         if not self.paid_amount:
    #             raise ValidationError(
    #                 _('Paid amount should have value when event type is [Paid]'.format(self.payment_type)))
    #         if not self.refundable_amount:
    #             raise ValidationError(
    #                 _('Refundable amount should have value when event type is [Paid]'.format(self.payment_type)))
    #     else:
    #         if not self.refundable_amount:
    #             raise ValidationError(
    #                 _('Refundable amount should have value when event type is [Free]'.format(self.payment_type)))

    @api.constrains('paid_attendee')
    def _check_participating_amount(self):
        if self.paid_attendee == 'yes':
            if not self.participating_amount:
                raise ValidationError(_('Participation Amount should have value when event type is [Yes]'))
        else:
            self.participating_amount = 0

    @api.multi
    def unlink(self):
        for reserve in self:
            if reserve.state != 'draft':
                raise ValidationError(_('[DELETE] Record cannot delete except draft state'))
        return super(EventReservation, self).unlink()

    @api.one
    def send_reservation(self):
        if self.state == 'reservation':
            """ create signup token for each user, and send their signup url by email """
            # prepare reset password signup
            create_mode = bool(self.env.context.get('create_user'))

            # no time limit for initial invitation, only for reset password
            expiration = False if create_mode else now(days=+1)

            self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

            # send email to users with their signup url
            template = False
            if create_mode:
                try:
                    template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
                except ValueError:
                    pass
            if not template:
                template = self.env.ref('auth_signup.reset_password_email')
            assert template._name == 'mail.template'

            template_values = {
                'email_to': '${object.email|safe}',
                'email_cc': False,
                'auto_delete': True,
                'partner_to': False,
                'scheduled_date': False,
            }
            template.write(template_values)

            for user in self:
                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                with self.env.cr.savepoint():
                    template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
                _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            self.state = 'draft'

    @api.one
    def act_draft(self):
        if self.state == 'reservation':
            self.state = 'draft'

    @api.one
    def act_reservation(self):
        if self.state == 'draft':
            self.state = 'reservation'

    @api.one
    def act_on_process(self):
        if self.state == 'reservation':
            self.state = 'on_process'

    @api.one
    def act_confirm(self):
        if self.state == 'on_process':
            vals = {
                'name': self.event_name,
                'organizer_id': self.poc_id.id,
                'poc_type_id': self.poc_type_id.id,
                'facilities_ids': [(4, rec.id) for rec in self.facilities_ids],
                'user_id': self.org_id.id,
                'event_type_id': self.event_type_id.id,
                'pillar_id': self.pillar_id.id,
                'theme_id': self.theme_id.id,
                'space_id': self.space_id,
                'expected_session': self.total_session,
                'request_date': self.request_date,
                'date_begin': self.start_date,
                'date_end': self.end_date,
                'last_date_reg': self.last_date_reg,
                'seats_availability': self.seats_availability,
                'seats_max': self.attendee_number,
                'mode_of_payment': self.mode_of_payment,
                'payment_type': self.payment_type,
                'date_of_payment': self.date_of_payment,
                'proposed_budget': self.proposed_budget,
                'approved_budget': self.approved_budget,
                'paid_amount': self.paid_amount,
                'refundable_amount': self.refundable_amount,
                'paid_attendee': self.paid_attendee,
                'participating_amount': self.participating_amount,
                'target_audience_group': self.target_audience_group,
                'target_age': self.target_age,
                'outreach_plan': self.outreach_plan,
                'outreach_plan_other': self.outreach_plan_other,
                'snacks_required': self.snacks_required,
                'description': self.description,
                'rules_regulation': self.rules_regulation,
                'notes': self.notes,
                'purpose_of_event': self.purpose_of_event,
                'ref_reservation': self.name,
                'event_mail_ids': [
                    (0, 0, {
                        'interval_unit': 'now',
                        'interval_type': 'after_sub',
                        'template_id': self.env['ir.model.data'].xmlid_to_res_id(
                            'event_registration.event_confirmation_registration')}),
                ]
            }
            event = self.env['event.event'].create(vals)
            if event:
                seq = self.env['ir.sequence'].next_by_code('event.reservation')
                self.write({
                    'name': seq,
                    'event_id': event.id
                })
                self._create_invoice()
                event.write({'state': 'draft'})
            self.state = 'confirm'

    @api.one
    def act_done(self):
        if self.state == 'confirm':
            self.state = 'done'

    @api.one
    def act_cancel(self):
        if self.state == 'draft':
            self.state = 'cancel'

    @api.model
    def _create_invoice(self):
        serv_name = ['Event Organization Fee', 'Event Refund Fee']
        services = self.env['product.product'].search([('name', 'in', serv_name), ('active', 'in', serv_name)],
                                                      order='id desc')
        if len(services) != 2:
            raise ValidationError(_('Please configure your event services.'))

        def create_invoice(service, vals):
            ins_inv = self.env['account.invoice']
            journal_id = self.env['account.journal'].search([('code', '=', 'INV')])
            account_id = self.env['account.account'].search(
                [('internal_type', '=', 'receivable'), ('deprecated', '=', False)])

            acc_invoice = {
                'partner_id': self.poc_id.id,
                'date_invoice': fields.datetime.now(),
                'date_due': datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S') - timedelta(days=1),
                'user_id': self.env.user.id,
                'origin': self.name,
                'account_id': account_id.id,
                'state': 'draft',
                'invoice_line_ids': [
                    (0, 0, {
                        'name': service.name,
                        'product_id': service.id,
                        'price_unit': vals['amount'],
                        'account_id': journal_id.default_debit_account_id.id,
                    })]
            }
            inv = ins_inv.create(acc_invoice)
            inv.action_invoice_open()

            if inv:
                self.state = 'confirm'
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
                vals = {
                    'template': 'mail_send.emk_inv_email_tmpl',
                    'email_to': self.poc_id.email,
                    'attachment_ids': [(6, 0, attachment.ids)],
                    'context': {
                        'name': self.poc_id.name,
                        'subject': vals['subject']
                    },
                }
                # self.env['mail.mail'].mailsend(vals)

        for ser in services:
            if ser.name == 'Event Organization Fee':
                if self.payment_type == 'paid':
                    if self.paid_amount == 0:
                        raise ValidationError(_("Please set paid amount which is required for paid event"))
                    vals = {
                        'amount': self.paid_amount,
                        'subject': 'Event Fee',
                    }
                    create_invoice(ser, vals)

            if ser.name == 'Event Refund Fee':
                if self.refundable_amount == 0:
                    raise ValidationError(_("Please set refundable amount which is required for free event."))
                vals = {
                    'amount': self.refundable_amount,
                    'subject': 'Refundable Amount',
                }

                create_invoice(ser, vals)

    @api.model
    def post_event_reservation(self, values, token=None):
        self.env['event.reservation'].create(values)

        # if token:
        #     # signup with a token: find the corresponding partner id
        #     partner = self.env['res.partner']._signup_retrieve_partner(token, check_validity=True, raise_exception=True)
        #     # invalidate signup token
        #     partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})
        #
        #     partner_user = partner.user_ids and partner.user_ids[0] or False
        #
        #     # avoid overwriting existing (presumably correct) values with geolocation data
        #     if partner.country_id or partner.zip or partner.city:
        #         values.pop('city', None)
        #         values.pop('country_id', None)
        #     if partner.lang:
        #         values.pop('lang', None)
        #
        #     if partner_user:
        #         # user exists, modify it according to values
        #         values.pop('login', None)
        #         values.pop('name', None)
        #         partner_user.write(values)
        #         return (self.env.cr.dbname, partner_user.login, values.get('password'))
        #     else:
        #         # user does not exist: sign up invited user
        #         values.update({
        #             'name': partner.name,
        #             'partner_id': partner.id,
        #             'email': values.get('email') or values.get('login'),
        #         })
        #         if partner.company_id:
        #             values['company_id'] = partner.company_id.id
        #             values['company_ids'] = [(6, 0, [partner.company_id.id])]
        #         self._signup_create_user(values)
        # else:
        #     # no token, sign up an external user
        #     values['email'] = values.get('email') or values.get('login')
        #     self._signup_create_user(values)
        #
        # return (self.env.cr.dbname, values.get('login'), values.get('password'))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'on_process', 'confirm'])]
