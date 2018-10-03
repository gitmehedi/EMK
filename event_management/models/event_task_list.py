# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventTaskList(models.Model):
    _name = 'event.task.list'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    task_duration = fields.Integer(string='Duration', required=True, track_visibility='onchange')
    task_description = fields.Text(string='Task Description', required=True, track_visibility='onchange')
    task_feedback = fields.Text(string='Task Feedback', required=True, track_visibility='onchange')
    assign_date = fields.Datetime(string="Assign Date", default=fields.Datetime.now, required=True,
                                  track_visibility='onchange')
    task_start = fields.Datetime(string='Task Start', track_visibility='onchange')
    task_stop = fields.Datetime(string='Task Stop', track_visibility='onchange')

    event_id = fields.Many2one('event.event', string='Event')
    assign_emp_id = fields.Many2one('res.partner', string='Assign To', required=True, track_visibility='onchange')
    task_id = fields.Many2one('event.task.type', string='Name', required=True, track_visibility='onchange')
    state = fields.Selection([('assign', 'Assigned'), ('start', 'Start'), ('finish', 'Finish')], default='assign',
                             track_visibility='onchange')

    # @api.onchange('room_id')
    # def onchange_room(self):
    #     if self.room_id:
    #         data = self.search([('room_id', '=', self.room_id.id), ('event_start', '<=', self.event_id.date_begin),
    #                             ('event_stop', '>=', self.event_id.date_begin), '|',
    #                             ('event_start', '<=', self.event_id.date_end),
    #                             ('event_stop', '>=', self.event_id.date_end)])
    #         if len(data) > 0:
    #             raise UserError(
    #                 _('[{0}] room already book for another event, please choose another.'.format(self.room_id.name)))
    #
    #         self.event_start = self.event_id.date_begin
    #         self.event_stop = self.event_id.date_end
    #
    # @api.constrains('room_id', 'event_start', 'event_stop')
    # def check_room(self):
    #     data = self.search([('room_id', '=', self.room_id.id), ('event_start', '<=', self.event_id.date_begin),
    #                         ('event_stop', '>=', self.event_id.date_begin), '|',
    #                         ('event_start', '<=', self.event_id.date_end),
    #                         ('event_stop', '>=', self.event_id.date_end)])
    #     if len(data) > 1:
    #         raise UserError(
    #             _('[{0}] room already book for another event, please choose another.'.format(self.room_id.name)))
