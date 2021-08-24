# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EventClose(models.Model):
    _name = 'event.close'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _rec_name = 'event_id'
    _description = 'Event Close'

    event_id = fields.Many2one('event.event', string='Event Name', required=True,
                               domain=[('state', '=', 'confirm')])
    event_type_id = fields.Many2one('event.type', string='Event Type', readonly=True,
                                    related='event_id.event_type_id')
    organizer_id = fields.Many2one('res.partner', string='Organizer Name', readonly=True,
                                   related='event_id.organizer_id')
    company_id = fields.Many2one('res.company', string="Organization Name", readonly=True,
                                 related='organizer_id.company_id')
    theme_id = fields.Many2one('res.users', string='Theme', readonly=True, states={'draft': [('readonly', False)]})
    audience_id = fields.Many2one('res.users', string='Key Audience', readonly=True,
                                  states={'draft': [('readonly', False)]})
    space_id = fields.Many2one('res.users', string='Space Used', readonly=True, states={'draft': [('readonly', False)]})
    event_associate_ids = fields.One2many('event.associate', 'event_close_id', string='Event associate', readonly=True,
                                          states={'draft': [('readonly', False)]})
    attachment_ids = fields.One2many('event.attachment', 'event_id', string="Attachment")
    contract_number = fields.Char(string="Contract Number", readonly=True,
                                  related='organizer_id.mobile')
    designation = fields.Char(string="Designation", readonly=True, related='organizer_id.function')
    work_email = fields.Char(string="Email", readonly=True, related='organizer_id.email')
    start_date = fields.Datetime(string='Start Date', readonly=True, related='event_id.date_begin')
    end_date = fields.Datetime(string='End Date', related='event_id.date_end', readonly=True)
    activity_duration = fields.Datetime(string='Activity Duration', readonly=True)
    total_participants = fields.Integer('Total Participants', compute='compute_total_participants', readonly=True,
                                        store=True)
    male_participants = fields.Integer('Total Male Participants', compute='compute_male_participants', readonly=True,
                                       store=True)
    female_participants = fields.Integer('Total Female Participants', compute='compute_female_participants',
                                         readonly=True, store=True)
    website = fields.Char('Website')
    attach_file = fields.Char('Attach a File')
    comment = fields.Text('Comments', track_visibility='onchange', readonly=True,
                          states={'draft': [('readonly', True)]})
    age_group = fields.Selection([('one', 'Below 18'), ('two', '18-35'), ('three', 'Over 18')], 'Age Group',
                                 readonly=True, states={'draft': [('readonly', False)]})
    non_usg = fields.Selection([('yes', 'Yes'), ('no', 'No')], readonly=True, states={'draft': [('readonly', True)]})
    event_summary = fields.Text('Summary of Event', track_visibility='onchange', readonly=True,
                                states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('approve', 'Approved'), ('close', 'Close'),
                              ('cancel', 'Canceled')], string="State", default="draft", track_visibility='onchange')

    @api.onchange('event_id')
    def onchange_event_associate_ids(self):
        self.event_associate_ids = []
        if self.event_id:
            vals = []
            line_obj = self.event_id.event_task_ids
            for record in line_obj:
                vals.append((0, 0, {
                    'associate_id': record.assign_emp_id.id,
                    'job_title': record.assign_emp_id.function,
                    'organization_id': record.assign_emp_id.company_id.id,

                }))
            self.event_associate_ids = vals

    @api.multi
    @api.depends('start_date', 'end_date')
    def compute_total_participants(self):
        self.total_participants = 10

    @api.multi
    @api.depends('start_date', 'end_date')
    def compute_male_participants(self):
        self.male_participants = 11

    @api.multi
    @api.depends('start_date', 'end_date')
    def compute_female_participants(self):
        self.female_participants = 12

    @api.one
    def act_cancel(self):
        if self.state == "confirm" or self.state == "approve":
            self.state = "cancel"

    @api.one
    def act_reset(self):
        if self.state == "confirm" or self.state == "approve":
            self.state = "draft"

    @api.multi
    def act_submit(self):
        if self.state == 'draft':
            vals = {
                'template': 'event_management.event_close_email_to_organizer_tmpl',
                'email_to': self.work_email if self.work_email else None,
                'context': {'organizer_name': self.organizer_id.name, 'event_name': self.event_id.name}
            }
            self.env['res.partner'].event_mailsend(vals)
            self.state = "confirm"

    @api.one
    def act_approve(self):
        if self.state == 'confirm':
            vals = {
                'template': 'event_management.event_clearance_email_to_organizer_tmpl',
                'email_to': self.work_email if self.work_email else None,
                'context': {'organizer_name': self.organizer_id.name, 'event_name': self.event_id.name}
            }
            self.env['res.partner'].event_mailsend(vals)
            self.state = "approve"

    @api.one
    def act_close(self):
        if self.state == 'approve':
            self.state = "close"
            self.event_id.button_done()

    @api.constrains('event_id')
    def _check_name(self):
        name = self.search([('event_id', '=ilike', self.event_id.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.multi
    def unlink(self):
        for event in self:
            if event.state != 'draft':
                raise ValidationError(_('You cannot delete a record which is not in draft state!'))
        return super(EventClose, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['approve', 'confirm'])]


class EventAssociate(models.Model):
    _name = "event.associate"

    event_close_id = fields.Many2one('event.close', string="Event Close")
    associate_id = fields.Many2one('res.partner', string='Name')
    job_title = fields.Char(string="Designation")
    organization_id = fields.Many2one('res.company', string="Organization")


class EventAttachment(models.Model):
    _name = 'event.attachment'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    filename = fields.Binary(string='Filename', required=True)
    event_id = fields.Many2one('event.close', string='Event')
