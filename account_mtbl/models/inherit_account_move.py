from odoo import models, fields, api, _


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    journal_id = fields.Many2one(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    ref = fields.Char(states={'posted': [('readonly', True)]},track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    narration = fields.Text(states={'posted': [('readonly', True)]},track_visibility='onchange')
    operating_unit_id = fields.Many2one(string='Branch',states={'posted': [('readonly', True)]},track_visibility='onchange')