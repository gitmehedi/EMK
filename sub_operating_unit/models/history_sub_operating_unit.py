# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class HistorySubOperatingUnit(models.Model):
    _name = 'history.sub.operating.unit'
    _description = 'History Sub Operating Unit'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    change_date = fields.Datetime(string='Date')
    line_id = fields.Many2one('sub.operating.unit', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approve'), ('reject', 'Reject')], default='pending')
