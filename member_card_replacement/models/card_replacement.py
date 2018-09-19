from odoo import models, fields, api, _


class MemberCardReplacement(models.Model):
    _name = 'member.card.replacement'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Member Card Replacement'
    _rec_name = 'name'

    name = fields.Char(string='Name', readonly=True)

    card_replacement_reason_id = fields.Many2one('member.card.replacement.reason', string='Card Replacement Reason',
                                                 required=True, track_visibility="onchange")
    membership_id = fields.Many2one("res.partner", string="Membership", required=True,
                                    readonly=True, states={'request': [('readonly', '=', False)]},
                                    track_visibility="onchange")
    request_date = fields.Date(string="Request Date", default=fields.Date.today(), required=True,
                               readonly=True, states={'request': [('readonly', '=', False)]},
                               track_visibility="onchange")
    authorize_date = fields.Date(string="Authenticate Date",
                                 readonly=True, states={'authenticate': [('readonly', '=', False)]},
                                 track_visibility="onchange")
    approve_date = fields.Date(string="Approve Date",
                               readonly=True, states={'approve': [('readonly', '=', False)]},
                               track_visibility="onchange")
    rejected_date = fields.Date(string="Rejected Date",
                                readonly=True, states={'approve': [('readonly', '=', False)]},
                                track_visibility="onchange")
    comments = fields.Text(string='Comments')

    state = fields.Selection(
        [('request', 'Request'), ('authenticate', 'Authenticate'), ('approve', 'Approve'), ('paid', 'Paid'),
         ('reject', 'Reject')],
        string="State", default='request', track_visibility="onchange")

    @api.one
    def act_request(self):
        if 'authenticate' in self.state:
            self.state = 'request'

    @api.one
    def act_authenticate(self):
        if 'request' in self.state:
            self.name = self.env['ir.sequence'].next_by_code('member.card.replacement.seq')
            self.authorize_date = fields.Date.today()
            self.state = 'authenticate'

    @api.one
    def act_approve(self):
        if self.state=='authenticate':
            self.approve_date = fields.Date.today()
            vals = {
                'template': 'member_card_replacement.member_card_replacement_approval_tmpl',
                'email_to': self.membership_id.email,
                'context': {'name': self.membership_id.name},
            }
            self.membership_id.mailsend(vals)
            self.state = 'approve'

    @api.one
    def act_reject(self):
        if self.state=='request':
            self.rejected_date = fields.Date.today()
            vals = {
                'template': 'member_card_replacement.member_card_replacement_cancel_tmpl',
                'email_to': self.membership_id.email,
                'context': {'name': self.membership_id.name},
            }
            self.membership_id.mailsend(vals)
            self.state = 'reject'

    @api.model
    def _needaction_domain_get(self):
        context = self.env.context
        if context.get('mcount') == 'request':
            return [('state', 'in', ['request'])]
        elif context.get('mcount') == 'authenticate':
            return [('state', 'in', ['authenticate'])]
        elif context.get('mcount') == 'approve':
            return [('state', 'in', ['approve'])]
