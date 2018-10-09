# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class EventClose(models.Model):
    _name = 'event.close'

    event_id = fields.Many2one('event.event',string='Event Name')
    event_type_id = fields.Many2one('event.type',string='Event Category',readonly=True,related='event_id.event_type_id')
    location_id = fields.Many2one('res.partner', string='Location', readonly=True,related='event_id.address_id')
    organizer_id = fields.Many2one('res.partner', string='Organizer', readonly=True,related='event_id.organizer_id')
    moderator_id = fields.Many2one('res.users', string='Location', readonly=True,related='event_id.user_id')
    #designation_id = fields.Many2one('hr.job', string="Moderator's Designation", readonly=True,related='moderator_id.job_id')
    #company_id = fields.Many2one('res.company', string="Moderator's Organization", readonly=True,related='moderator_id.company_id')
    theme_id = fields.Many2one('res.users', string='Theme')
    audience_id = fields.Many2one('res.users', string='Key Audience')
    #mobile_phone = fields.Char(string="Moderator's Contract Number", readonly=True,related='moderator_id.mobile_phone')
    #work_email = fields.Char(string="Moderator's Email", readonly=True,related='moderator_id.work_email')
    start_date = fields.Datetime(string='Start Date',readonly=True,related='event_id.date_begin')
    end_date = fields.Datetime(string='End Date',related='event_id.date_end',readonly=True)
    activity_duration = fields.Datetime(string='Activity Duration', readonly=True)
    total_participants = fields.Integer('Total Number of Participants')
    male_participants = fields.Integer('Total Number of Male Participants')
    female_participants = fields.Integer('Total Number of FeMale Participants')
    website = fields.Char('Website')
    attach_file = fields.Char('Attach')
    comment= fields.Char('Comments')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('approve', 'Approved'),
                              ('cancel', 'Canceled')], string="State", default="draft")
    age_group = fields.Selection([('one', 'Below 18'),
                                  ('two', '18-35'),
                                  ('three', 'Over 18')], 'Age Group')
    non_usg = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')])
    event_summary = fields.Char('Summary of event')