# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventTaskList(models.Model):
    _name = 'event.task.list'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'task_id'

    task_duration = fields.Float(string='Duration', required=True, track_visibility='onchange', readonly=True,
                                   states={'draft': [('readonly', False)]})
    task_description = fields.Text(string='Task Description', required=True, track_visibility='onchange', readonly=True,
                                   states={'draft': [('readonly', False)]})
    task_feedback = fields.Text(string='Task Feedback',  track_visibility='onchange', readonly=True,
                                states={'start': [('readonly', False)]})
    assign_date = fields.Datetime(string="Assign Date", track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    task_start = fields.Datetime(string='Task Start', track_visibility='onchange', readonly=True,
                                 states={'assign': [('readonly', False)]})
    task_stop = fields.Datetime(string='Task Stop', track_visibility='onchange', readonly=True,
                                states={'start': [('readonly', False)]})

    event_id = fields.Many2one('event.event', string='Event', readonly=True, required=True,
                               states={'draft': [('readonly', False)]})
    assign_emp_id = fields.Many2one('res.partner', string='Assign To', required=True, track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False)]})
    task_id = fields.Many2one('event.task.type', string='Task Name', required=True, track_visibility='onchange',
                              domain=[('status','=',True)],
                              readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('assign', 'Assigned'), ('start', 'Start'), ('finish', 'Finish')],
                             default='draft', track_visibility='onchange')

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['assign', 'start'])]

    @api.one
    def act_draft(self):
        if self.state == 'assign':
            self.state = 'draft'

    @api.one
    def act_assign(self):
        if self.state == 'draft':
            self.assign_date = fields.Datetime.now()
            self.state = 'assign'

    @api.one
    def act_start(self):
        if self.state == 'assign':
            self.task_start = fields.Datetime.now()
            self.state = 'start'

    @api.one
    def act_finish(self):
        if self.state == 'start':
            self.task_stop = fields.Datetime.now()
            self.state = 'finish'
