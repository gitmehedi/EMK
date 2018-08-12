from odoo import models, fields, api, _


class MemberCardReplacement(models.Model):
    _name = 'member.card.replacement'
    _description = 'Member Card Replacement'

    membership_id = fields.Many2one("res.partner", string="Membership", required=True,
                                    readonly=True, states={'request': [('readonly', '=', False)]})
    request_date = fields.Date(string="Request Date", default=fields.Date.today(), required=True,
                               readonly=True, states={'request': [('readonly', '=', False)]})
    authorize_date = fields.Date(string="Authenticate Date",
                                 readonly=True, states={'authenticate': [('readonly', '=', False)]})
    approve_date = fields.Date(string="Approve Date",
                               readonly=True, states={'approve': [('readonly', '=', False)]})
    state = fields.Selection(
        [('request', 'Request'), ('authenticate', 'Authenticate'), ('approve', 'Approve'), ('paid', 'Paid'),
         ('reject', 'Reject')],
        string="State", default='request')

    @api.one
    def act_request(self):
        if 'authenticate' in self.state:
            self.state = 'request'

    @api.one
    def act_authenticate(self):
        if 'request' in self.state:
            self.state = 'authenticate'

    @api.one
    def act_paid(self):
        if 'approve' in self.state:
            self.state = 'paid'
