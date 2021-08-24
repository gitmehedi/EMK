# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventReservation(models.Model):
    _name = 'event.reservation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'organizer_id'
    _order = 'id desc'
    _description = 'Event Reservation'

    name = fields.Char(string='Name', readonly=True, states={'draft': [('readonly', False)]})
    event_name = fields.Char(string='Event Name', required=True, readonly=True, states={'draft': [('readonly', False)]})

    organizer_id = fields.Many2one('res.partner', string='Organizer Name', domain=[('is_organizer', '=', True)],
                                   default=False, required=True, track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False)]})
    event_type_id = fields.Many2one('event.type', string='Event Type', required=True, track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False)]})
    event_id = fields.Many2one('event.event', string='Event', track_visibility='onchange', readonly=True)
    org_type_id = fields.Many2one('event.organization.type', string="Organization Type", required=True,
                                  track_visibility='onchange',
                                  readonly=True, states={'draft': [('readonly', False)]})
    facilities_ids = fields.Many2many('event.task.type', string="Facilities Requested",
                                      track_visibility='onchange',
                                      readonly=True, states={'draft': [('readonly', False)]})
    contact_number = fields.Char(string="Contact Number", readonly=True, related='organizer_id.mobile')
    work_email = fields.Char(string="Email", readonly=True, related='organizer_id.email')

    attendee_number = fields.Integer('No. of Attendees', required=True, track_visibility='onchange',
                                     readonly=True, states={'draft': [('readonly', False)]})
    total_session = fields.Integer('No. of Sessions', required=True, track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False)]})
    start_date = fields.Datetime(string='Start Date', required=True, track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Datetime(string='End Date', required=True, track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False)]})
    request_date = fields.Datetime(string='Requested Date', required=True, track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Html('Description', track_visibility='onchange', required=True, sanitize=False,
                              readonly=True, states={'draft': [('readonly', False)]})

    payment_type = fields.Selection([('free', 'Free'), ('paid', 'Paid')], required=True, default='free', string='Type',
                                    readonly=True, states={'draft': [('readonly', False)]})
    mode_of_payment = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], required=True, default='cash',
                                       string='Mode Of Payment', track_visibility='onchange',
                                       readonly=True, states={'draft': [('readonly', False)]})
    paid_amount = fields.Float(string='Paid Amount', digits=(12, 2), track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False)]})
    refundable_amount = fields.Float(string='Refundable Amount', digits=(12, 2), track_visibility='onchange',
                                     required=True,
                                     readonly=True, states={'draft': [('readonly', False)]})
    rules_regulation = fields.Html(string='Rules and Regulation', track_visibility='onchange', sanitize=True,
                                   readonly=True, states={'draft': [('readonly', False)]})
    date_of_payment = fields.Date(string="Expected Date for Payment", track_visibility='onchange',
                                  readonly=True, states={'draft': [('readonly', False)]})
    notes = fields.Html(string="Comments/Notes", track_visibility='onchange', sanitize=False,
                        readonly=True, states={'draft': [('readonly', False)]})
    paid_attendee = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                     string="Participation Charge", readonly=True,
                                     states={'draft': [('readonly', False)]})
    participating_amount = fields.Integer(string="Participation Amount", readonly=True,
                                          states={'draft': [('readonly', False)]})
    space_id = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string="Do you need EMK Space?",
                                readonly=True, states={'draft': [('readonly', False)]})
    seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')], readonly=True,
                                          string='Available Seat', default="limited",
                                          states={'draft': [('readonly', False)]})
    image_medium = fields.Binary(string='Photo', attachment=True, readonly=True,
                                 states={'draft': [('readonly', False)]})

    state = fields.Selection(
        [('draft', 'Draft'), ('on_process', 'On Process'), ('confirm', 'Confirmed'), ('done', 'Done'),
         ('cancel', 'Cancelled')], string="State", default="draft", track_visibility='onchange')

    @api.multi
    @api.constrains('date_begin')
    def _check_date_begin(self):
        dt_now = fields.datetime.now()
        date_begin = datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)
        if date_begin < dt_now:
            raise ValidationError(_("Event start date cannot be past date from current date"))

    @api.constrains('event_name')
    def _check_name(self):
        name = self.search([('event_name', '=ilike', self.event_name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.multi
    def unlink(self):
        for reserve in self:
            if reserve.state != 'draft':
                raise ValidationError(_('You cannot delete a record which is not in draft state!'))
        return super(EventReservation, self).unlink()

    @api.one
    def act_draft(self):
        if self.state == 'on_process':
            self.state = 'draft'

    @api.one
    def act_on_process(self):
        if self.state == 'draft':
            self.state = 'on_process'

    @api.one
    def act_confirm(self):
        if self.state == 'on_process':
            vals = {
                'name': self.event_name,
                'organizer_id': self.organizer_id.id,
                'event_type_id': self.event_type_id.id,
                'date_begin': self.start_date,
                'date_end': self.end_date,
                'payment_type': self.payment_type,
                'mode_of_payment': self.mode_of_payment,
                'paid_amount': self.paid_amount,
                'participating_amount': self.participating_amount,
                'refundable_amount': self.refundable_amount,
                'date_of_payment': self.date_of_payment,
                'seats_max': self.attendee_number,
                'seats_availability': self.seats_availability,
                'description': self.description,
                'rules_regulation': self.rules_regulation,
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
        serivces = self.env['product.product'].search([('name', 'in', serv_name), ('active', 'in', serv_name)],
                                                      order='id desc')
        if len(serivces) != 2:
            raise ValidationError(_('Please configure your event services.'))

        def create_invoice(service, vals):
            ins_inv = self.env['account.invoice']
            journal_id = self.env['account.journal'].search([('code', '=', 'INV')])
            account_id = self.env['account.account'].search(
                [('internal_type', '=', 'receivable'), ('deprecated', '=', False)])

            acc_invoice = {
                'partner_id': self.organizer_id.id,
                'date_invoice': fields.datetime.now(),
                'date_due': datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S') - timedelta(days=1),
                'user_id': self.env.user.id,
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
                    'email_to': self.organizer_id.email,
                    'attachment_ids': [(6, 0, attachment.ids)],
                    'context': {
                        'name': self.organizer_id.name,
                        'subject': vals['subject']
                    },
                }
                # self.env['mail.mail'].mailsend(vals)

        for ser in serivces:
            if ser.name == 'Event Organization Fee':
                if self.payment_type == 'paid':
                    if self.paid_amount == 0:
                        raise ValidationError(_("Please set paid amount which is required for paid event"))
                    vals = {
                        'amount': self.paid_amount,
                        'subject': 'Event Fee',
                    }

            if ser.name == 'Event Refund Fee':
                if self.refundable_amount == 0:
                    raise ValidationError(_("Please set refundable amount which is required for free event."))
                vals = {
                    'amount': self.refundable_amount,
                    'subject': 'Refundable Amount',
                }

            create_invoice(ser, vals)

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'on_process', 'confirm'])]
