from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    journal_id = fields.Many2one(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    ref = fields.Char(states={'posted': [('readonly', True)]}, track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    narration = fields.Text(states={'posted': [('readonly', True)]}, track_visibility='onchange')
    partner_id = fields.Many2one(string='Vendor')
    operating_unit_id = fields.Many2one(string='Branch', track_visibility='onchange',
                                        states={'posted': [('readonly', True)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    is_cbs = fields.Boolean(default=False, help='CBS data always sync with OGL using GLIF.')
    is_sync = fields.Boolean(default=False, help='OGL continuously send data to CBS for journal sync.')
    is_cr = fields.Boolean(default=False)
    user_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')

    @api.multi
    def post(self):
        if self.env.user.id == self.user_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        return super(AccountMove, self).post()

    @api.constrains('date')
    def _check_date(self):
        if self.date > fields.Datetime.now():
            raise ValidationError(_('Journal Date should not be greater than current datetime.'))


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    name = fields.Char(string="Narration")
    account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)])
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string="Sub Operating Unit")
    segment_id = fields.Many2one('segment', string="Segment")
    acquiring_channel_id = fields.Many2one('acquiring.channel', string="AC")
    servicing_channel_id = fields.Many2one('servicing.channel', string="SC")
    operating_unit_id = fields.Many2one(string='Branch')
