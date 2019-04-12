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


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string="Sub Branch")
    segment_id = fields.Many2one('segment', string="Segment")
    acquiring_channel_id = fields.Many2one('acquiring.channel', string="AC")
    servicing_channel_id = fields.Many2one('servicing.channel', string="SC")
    operating_unit_id  = fields.Many2one(string='Branch')
