# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventEvent(models.Model):
    _inherit = 'event.event'
    _order = 'id desc'

    organizer_id = fields.Many2one('res.partner', string='PoC Name', domain=[('is_poc', '=', True)],
                                   default=False, required=True, readonly=False, states={'done': [('readonly', True)]})
    contact_number = fields.Char(string="Contact Number", readonly=True, related='organizer_id.mobile')
    work_email = fields.Char(string="Email", readonly=True, related='organizer_id.email')
    event_type_id = fields.Many2one(string="Event Type", required=True)
    poc_type_id = fields.Many2one('event.poc.type', string="PoC Type", required=True,
                                  track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one(string="Organizer Name", required=True)
    pillar_id = fields.Many2one('event.pillar', string='Event Pillar', track_visibility='onchange', required=True,
                                readonly=True, states={'draft': [('readonly', False)]})
    theme_id = fields.Many2one('event.theme', string='Event Theme', track_visibility='onchange', required=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    last_date_reg = fields.Datetime(string='Last Date of Registration', required=True, track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False)]})
    facilities_ids = fields.Many2many('event.task.type', string="Facilities Requested", track_visibility='onchange',
                                      required=True, readonly=True, states={'draft': [('readonly', False)]})
    total_seat_available = fields.Integer(string="Total Seat Available", compute='compute_total_seat')
    event_book_ids = fields.One2many('event.room.book', 'event_id', string='Event Rooms', readonly=False,
                                     states={'done': [('readonly', True)]})
    event_task_ids = fields.One2many('event.task.list', 'event_id', string='Event Tasks', readonly=False,
                                     states={'done': [('readonly', True)]})
    date_begin = fields.Datetime(string='Start Date', required=True, track_visibility='onchange',
                                 states={'confirm': [('readonly', True)], 'done': [('readonly', True)]})
    payment_type = fields.Selection([('paid', 'Paid'), ('free', 'Free')], required=True,
                                    default='free', string='Type',
                                    readonly=False, states={'done': [('readonly', True)]})
    mode_of_payment = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], required=True, default='cash',
                                       readonly=False, states={'done': [('readonly', True)]},
                                       string='Mode of Payment')
    approved_budget = fields.Float(string='Approved Budget', digits=(12, 2), track_visibility='onchange',
                                   required=True, readonly=True, states={'draft': [('readonly', False)]})
    proposed_budget = fields.Float(string='Proposed Budget', digits=(12, 2), track_visibility='onchange',
                                   required=True, readonly=True, states={'draft': [('readonly', False)]})
    paid_amount = fields.Float(string='Paid Amount', digits=(12, 2), readonly=False,
                               states={'done': [('readonly', True)]})
    paid_attendee = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                     string="Participation Charge", readonly=True, required=True,
                                     states={'draft': [('readonly', False)]})
    refundable_amount = fields.Float(string='Refundable Amount', digits=(12, 2), readonly=False,
                                     states={'done': [('readonly', True)]})
    rules_regulation = fields.Html(string='Rules and Regulation', readonly=False, states={'done': [('readonly', True)]})
    date_of_payment = fields.Date(string="Expected Date for Payment", readonly=False, required=True,
                                  states={'done': [('readonly', True)]})
    notes = fields.Html(string="Comments/Notes", readonly=False, states={'done': [('readonly', True)]})
    ref_reservation = fields.Char(string="Reservation Reference", readonly=False, states={'done': [('readonly', True)]})
    image_medium = fields.Binary(string='Medium-sized photo', attachment=True)
    participating_amount = fields.Integer(string="Participation Amount", readonly=True,
                                          states={'confirm': [('readonly', False)]})
    expected_session = fields.Integer(string="No. of Sessions", readonly=True)
    purpose_of_event = fields.Html(string="Purpose of Event", track_visibility='onchange', sanitize=False,
                                   readonly=True, states={'draft': [('readonly', False)]})
    target_audience_group = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', required=True,
                                             string="Target Audience Group", readonly=True,
                                             states={'draft': [('readonly', False)]})
    target_age = fields.Integer(string="Target Age", required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    outreach_plan = fields.Selection([('social_media', 'Social Media Promotions'),
                                      ('press_coverage', 'Press Coverage'),
                                      ('designing', 'Designing'),
                                      ('others', 'Others'),
                                      ], string="Outreach Plan", required=True, readonly=True,
                                     states={'draft': [('readonly', False)]})
    outreach_plan_other = fields.Char(string="Outreach Plan Other", readonly=True,
                                      states={'draft': [('readonly', False)]})
    snacks_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes',
                                       string="Food/Beverage/Snacks?", readonly=True,
                                       states={'draft': [('readonly', False)]})
    space_id = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string="Need EMK Space?",
                                readonly=True, required=True, states={'draft': [('readonly', False)]})
    seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')], required=True,
                                          readonly=True, string='Available Seats', default="limited",
                                          states={'draft': [('readonly', False)]})
    seats_min = fields.Integer(string='Min Attendees')
    seats_max = fields.Integer(string='Max Attendees')

    @api.depends('event_book_ids')
    def compute_total_seat(self):
        for record in self:
            record.total_seat_available = sum([rec.seat_no for rec in record.event_book_ids])

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
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.one
    def button_done(self):

        if self.state == 'confirm':
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
        return [('state', 'in', ['confirm', 'draft'])]


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    date_of_birth = fields.Date(string='Date of Birth')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True,
                              default='male', string='Gender')
    profession_id = fields.Many2one('attendee.profession', string='Profession', default=False)
    card_number = fields.Char(string='Card Number')

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'open'])]


class AttendeeProfession(models.Model):
    _name = 'attendee.profession'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = 'Attendee Profession'

    name = fields.Char(string='Profession', required=True)
    status = fields.Boolean(default=True)
