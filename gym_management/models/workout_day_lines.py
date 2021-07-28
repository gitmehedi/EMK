# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class GymDay(models.Model):
    _name = 'gym.day'
    _rec_name = 'day'
    
    day=fields.Datetime(
        'Date'
    )
    is_done = fields.Boolean(
        'Is Done'
    )
    workout_schedule_id = fields.Many2one(
        'gym.workout'
    )
    state = fields.Selection(
        selection=[
            ('new','New'),
            ('done','Done'),
            ('cancle','Cancle'),
        ],
        string ="Status",
        default =lambda self: _('new'),
    )
    
    @api.multi
    def done(self):
        self.state = 'done'
    
    @api.multi
    def cancle(self):
        self.state = 'cancle'
        
    @api.multi
    def reset(self):
        self.state = 'new'

