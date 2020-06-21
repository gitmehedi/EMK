# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread', 'ir.needaction_mixin']

    state = fields.Selection(track_visibility='onchange',change_default=True,)




