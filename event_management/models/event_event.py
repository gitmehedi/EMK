# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.addons.event_management.data import helper
from odoo.addons.opa_utility.helper.utility import Message
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError


class EventEvent(models.Model):
    _inherit = 'event.event'
    _order = 'id desc'

    name = fields.Char(readonly=True, states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    organizer_id = fields.Many2one('res.partner', string='PoC Name', domain=[('is_poc', '=', True)],
                                   default=False, required=True, readonly=True,
                                   states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    contact_number = fields.Char(string="Contact Number", readonly=True, related='organizer_id.mobile',
                                 states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    work_email = fields.Char(string="Email", readonly=True, related='organizer_id.email')
    event_type_id = fields.Many2one(string="Event Type", required=True, readonly=True,
                                    states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    poc_type_id = fields.Many2one('event.poc.type', string="PoC Type", required=True,
                                  track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    user_id = fields.Many2one(string="Organizer Name", required=True, readonly=True,
                              states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    pillar_id = fields.Many2one('event.pillar', string='Event Pillar', track_visibility='onchange', required=True,
                                readonly=True,
                                states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    theme_id = fields.Many2one('event.theme', string='Event Theme', track_visibility='onchange', required=True,
                               readonly=True,
                               states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    last_date_reg = fields.Datetime(string='Last Date of Registration', required=True, track_visibility='onchange',
                                    readonly=True,
                                    states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    request_date = fields.Datetime(string='Request Date', required=True, track_visibility='onchange',
                                   readonly=True,
                                   states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    facilities_ids = fields.Many2many('event.service.type', string="Facilities Requested", track_visibility='onchange',
                                      required=True, readonly=True,
                                      states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    invoice_ids = fields.Many2many('account.invoice', string="Invoices", track_visibility='onchange',readonly=True,
                                      states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')
    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Rooms', readonly=True,
                                     states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    event_task_ids = fields.One2many('event.task.list', 'event_id', string='Event Tasks', readonly=True,
                                     states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    date_begin = fields.Datetime(string='Start Date', required=True, track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    payment_type = fields.Selection(helper.payment_type, required=True,
                                    default='free', string='Type', readonly=True,
                                    states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    mode_of_payment = fields.Many2one('account.journal', string='Mode of Payment', required=True,
                                      track_visibility='onchange', domain=[('type', 'in', ['bank', 'cash'])],
                                      readonly=True,
                                      states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    approved_budget = fields.Float(string='Approved Budget', digits=(12, 2), track_visibility='onchange',
                                   required=True, readonly=True,
                                   states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    proposed_budget = fields.Float(string='Proposed Budget', digits=(12, 2), track_visibility='onchange',
                                   required=True, readonly=True,
                                   states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    paid_amount = fields.Float(string='Paid Amount', digits=(12, 2), readonly=True,
                               states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    paid_attendee = fields.Selection(helper.paid_attendee, default='yes', readonly=True, required=True,
                                     string="Participation Charge",
                                     states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    refundable_amount = fields.Float(string='Refundable Amount', digits=(12, 2), readonly=True,
                                     states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    rules_regulation = fields.Html(string='Rules and Regulation', readonly=True,
                                   states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    description = fields.Html(readonly=True,
                              states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    date_of_payment = fields.Date(string="Expected Date for Payment", readonly=True,
                                  states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    notes = fields.Html(string="Comments/Notes", readonly=True,
                        states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    ref_reservation = fields.Char(string="Reservation Reference", readonly=True,
                                  states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    image_medium = fields.Binary(string='Medium-sized photo', attachment=True, readonly=True,
                                 states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    participating_amount = fields.Integer(string="Participation Amount", readonly=True,
                                          states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    expected_session = fields.Integer(string="No. of Sessions", readonly=True,
                                      states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    purpose_of_event = fields.Html(string="Purpose of Event", track_visibility='onchange', sanitize=False,
                                   readonly=True,
                                   states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    target_audience_group = fields.Char(string="Target Audience Group", readonly=True,
                                        states={'draft': [('readonly', False)],
                                                'mark_close': [('readonly', False)]})
    target_age = fields.Char(string="Target Age", required=True, readonly=True,
                             states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    outreach_plan = fields.Many2many('event.outreach.plan', string="Outreach Plan", readonly=True,
                                     states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    outreach_plan_other = fields.Char(string="Outreach Plan Other", readonly=True,
                                      states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    snacks_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                       string="Food/Beverage/Snacks?", readonly=True,
                                       states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    space_id = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string="Need EMK Space?",
                                required=True, readonly=True,
                                states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')], required=True,
                                          string='Available Seats', default="limited", readonly=True,
                                          states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    seats_min = fields.Integer(string='Min Attendees', readonly=True,
                               states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    seats_max = fields.Integer(string='Max Attendees', readonly=True,
                               states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    date_end = fields.Datetime(readonly=True,
                               states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    event_category_id = fields.Many2one('event.category', string='Event Category', track_visibility='onchange',
                                        readonly=True,states={'draft': [('readonly', False)], 'mark_close': [('readonly', False)]})
    event_share_name = fields.Char()
    event_share = fields.Binary(string="Event Details", attachment=True, track_visibility='onchange',
                                readonly=True, states={'draft': [('readonly', False)],
                                        'approve': [('readonly', False)]})
    total_participation_amount = fields.Float(string="Total Participation Amount", compute='compute_total_collection')
    state = fields.Selection(helper.event_state, string="State")
    close_registration = fields.Selection([('open', 'Open'), ('close', 'Close')], string='Close Registration',
                                          track_visibility='onchange', readonly=True, default='open')
    social_content_ids = fields.One2many('event.social.content.reservation', 'line_id',readonly=True,
                                         states={'draft': [('readonly', False)],
                                                 'reservation': [('readonly', False), ('required', True)]})

    @api.depends('event_book_ids')
    def compute_total_seat(self):
        for record in self:
            record.total_seat_available = sum([rec.seat_no for rec in record.event_book_ids])

    @api.depends('event_book_ids')
    def compute_total_collection(self):
        for record in self:
            record.total_participation_amount = sum([reg.event_fee for reg in record.registration_ids])

    # @api.onchange('event_book_ids')
    # def onchange_event_book_ids(self):
    #     if self.facilities_ids:
    #         room = self.env['event.room'].search([('service_ids','in',self.facilities_ids.ids)])
    #
    #
    #     self.facilities_ids.ids
    #     return True

    @api.multi
    @api.constrains('date_begin')
    def _check_date_begin(self):
        dt_now = fields.datetime.now()
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=1)
        if date_begin < dt_now:
            raise ValidationError(_("Event start date cannot be past date from current date"))

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.one
    def button_done(self):
        if self.state == 'mark_close':
            message = ''
            rooms = [room.state for room in self.event_book_ids if room.state == 'assign']
            if len(rooms) > 0:
                message += '- Registered room still in open status, either close or cancel. \n'

            regs = [reg.state for reg in self.registration_ids if reg.state == 'open']
            if len(regs) > 0:
                message += '- Registered participant still in open status, either close or cancel. \n'

            tasks = [task.state for task in self.event_task_ids if task.state == 'draft']
            if len(tasks) > 0:
                message += '- Assign task still in open status, either close or cancel. \n'

            sess = [ses.state for ses in self.session_ids if ses.state in ['unconfirmed', 'confirmed']]
            if len(sess) > 0:
                message += '- Registered sessions still in open status, either close or cancel. \n'

            if len(message) > 0:
                msg = "Review mention point in event [{0}]\n\n".format(self.display_name) + message
                raise ValidationError(_(msg))
            else:
                self.state = "done"
                return True
        else:
            raise ValidationError(_("Event not in confirm state, please check event [{0}]".format(self.display_name)))

    @api.one
    def act_mark_close(self):
        if self.state == 'confirm':
            self.state = 'mark_close'

    @api.one
    def button_approve(self):
        if self.state == 'draft':
            self.state = 'approve'

    @api.one
    def button_confirm(self):
        self.state = 'confirm'

    @api.multi
    def unlink(self):
        for event in self:
            if event.state == 'done':
                raise ValidationError(_('You cannot delete a record which is not in draft state!'))
        return super(EventEvent, self).unlink()

    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for event in self:
            date_begin = fields.Datetime.from_string(event.date_begin)
            date_end = fields.Datetime.from_string(event.date_end)
            dates = [fields.Date.to_string(fields.Datetime.context_timestamp(event, dt)) for dt in
                     [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((event.id, '%s [%s]' % (event.name, ' - '.join(dates))))
        return result

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['confirm', 'draft', 'mark_close', 'close'])]


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    date_of_birth = fields.Date(string='Date of Birth')
    gender = fields.Many2one('res.gender', required=True, string='Gender')
    profession_id = fields.Many2one('attendee.profession', string='Profession', default=False)
    card_number = fields.Char(string='Card Number')
    event_fee = fields.Float(string='Event Participation Amount')

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'open'])]

    @api.one
    def button_reg_close(self):
        res = super(EventRegistration, self).button_reg_close()
        self.write({'event_fee': self.event_id.participating_amount})


class AttendeeProfession(models.Model):
    _name = 'attendee.profession'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = 'Attendee Profession'

    name = fields.Char(string='Profession', required=True)
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Message.UNLINK_WARNING))
            try:
                return super(AttendeeProfession, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))


class EventSocialContentReservation(models.Model):
    _name = 'event.social.content.reservation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Event Social Content'

    name = fields.Char('Content Title', required=True, translate=True, track_visibility='onchange')
    content = fields.Binary('Content Upload', translate=True, track_visibility='onchange')
    content_description = fields.Char('Content Description', translate=True, track_visibility='onchange')
    line_id = fields.Many2one('event.event', ondelete='cascade', translate=True, track_visibility='onchange')
