from odoo import models, fields, api, _


class RenewRequest(models.Model):
    _name = 'renew.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'membership_id'
    _order = 'id desc'

    membership_id = fields.Many2one('res.partner', string='Name', required=True,
                                    readonly=True, states={'request': [('readonly', False)]})
    request_date = fields.Date(string='Requst Date', default=fields.Date.today(), required=True,
                               readonly=True, states={'request': [('readonly', False)]})

    approve_date = fields.Date(string='Approve Date', default=fields.Date.today(),
                               readonly=True, states={'request': [('readonly', False)]})
    state = fields.Selection([('request', 'Request'), ('invoice', 'Invoiced'), ('done', 'Done'), ('reject', 'Reject')],
                             default='request', string='State')

    @api.one
    def act_invoice(self):
        if 'request' in self.state:
            self.membership_id._create_invoice()
            self.state = 'invoice'

    @api.one
    def act_done(self):
        if 'invoice' in self.state:
            self.state = 'done'

    @api.one
    def act_reject(self):
        if 'request' in self.state:
            self.state = 'reject'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'request')]
