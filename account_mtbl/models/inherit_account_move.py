from odoo import models, fields, api, _


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    journal_id = fields.Many2one(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    ref = fields.Char(track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    operating_unit_id = fields.Many2one(track_visibility='onchange')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string="Sub Operating Unit",
                                            track_visibility='onchange',
                                            readonly=True, states={'draft': [('readonly', False)]})
    segment_id = fields.Many2one('segment', string="Segment",track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]})
    acquiring_channel_id = fields.Many2one('acquiring.channel', string="Acquiring Channel",track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]})
    servicing_channel_id = fields.Many2one('servicing.channel', string="Servicing Channel",track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]})
    bank_id = fields.Many2one('res_bank', string="Bank",track_visibility='onchange',
                                           readonly=True, states={'draft': [('readonly', False)]})
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Center',
                                          ondelete="cascade",track_visibility='onchange',
                                          readonly=True, states={'draft': [('readonly', False)]})