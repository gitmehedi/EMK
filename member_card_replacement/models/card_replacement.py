from odoo import models, fields, api, _


class MemberCardReplacement(models.Model):
    _name = 'member.card.replacement'
    _inherit = ['ir.needaction_mixin']
    _description = 'Member Card Replacement'
    _rec_name = 'membership_id'

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
    def act_approve(self):
        if 'authenticate' in self.state:
            self.state = 'approve'

    @api.one
    def act_paid(self):
        if 'approve' in self.state:
            self.state = 'paid'

    @api.one
    def act_reject(self):
        if 'request' in self.state:
            # implement mail functionality for mail
            # mailobj={
            #
            # }
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
