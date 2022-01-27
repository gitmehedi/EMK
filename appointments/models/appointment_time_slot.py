from odoo import api, fields, models, _
from odoo.addons.appointments.helpers import functions
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError

DAYS = [
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
]


class AppointmentTimeSlot(models.Model):
    _name = 'appointment.timeslot'
    _description = "Appointment Time Slot"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"
    _rec_name = "name"

    name = fields.Char(string="Time Slot", readonly=True, copy=False, track_visibility='onchange',
                       compute='_compute_name')
    day = fields.Selection(DAYS, 'Day', required=True, track_visibility="onchange")
    start_time = fields.Float(string="Start Time", required=True, digits=(2, 2), track_visibility="onchange")
    end_time = fields.Float(string="End Time", required=True, digits=(2, 2), track_visibility="onchange")
    description = fields.Text(string="Description", track_visibility="onchange")
    contact_ids = fields.Many2many('appointment.contact', 'contact_timeslot_relation', 'contact_id', 'timeslot_id',
                                   string="Time Slot")
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.multi
    @api.depends('day', 'start_time', 'end_time')
    def _compute_name(self):
        for rec in self:
            if rec.day and rec.start_time and rec.end_time:
                start_time = functions.float_to_time(rec.start_time)
                end_time = functions.float_to_time(rec.end_time)
                rec.name = '%s [%s - %s] ' % (rec.day.title(), start_time, end_time)

    @api.constrains('name', 'start_time', 'end_time')
    def _check_name(self):
        name = self.search([('day', '=', self.day), ('start_time', '=', self.start_time),
                            ('end_time', '=', self.end_time)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.constrains('start_time', 'end_time')
    def _check_max_min(self):
        for rec in self:
            if functions.float_to_time(rec.end_time) <= functions.float_to_time(rec.start_time):
                raise ValidationError(_("Start Time should not be greater than End Time."))

    @api.constrains('start_time', 'end_time')
    def _check_valid_time(self):
        if functions.float_to_time(self.start_time) < '00:00' or functions.float_to_time(self.start_time) > '23:59':
            raise ValidationError(_("Start Time should be valid date time"))
        if functions.float_to_time(self.end_time) < '00:00' or functions.float_to_time(self.end_time) > '23:59':
            raise ValidationError(_("End Time should be valid date time"))

    @api.constrains('start_time', 'end_time', 'day')
    def check_time_intersect(self):
        query = """select id,day,start_time,end_time from appointment_timeslot 
        WHERE (start_time <= %s and %s <= end_time) and active=True
        and day = '%s'""" % (self.end_time, self.start_time, self.day)

        # self._cr.execute(query, tuple([self.end_time, self.start_time, self.day]))
        self.env.cr.execute(query)
        for val in self.env.cr.fetchall():
            "{0}:{1}-{2}:{3}".format(val[0], val[1], val[2], val[3])
        # if rec:
        #     raise ValidationError(_('[Warning] Time should not be overlap at same day.'))
        # for val in rec:
            if val[0]:
                raise ValidationError(_('[Warning] Time should not be overlap at same day.'))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('day', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

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
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))
            try:
                return super(AppointmentTimeSlot, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))
