from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class RenewRequest(models.Model):
    _name = 'renew.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Membership Renew Request'
    _rec_name = 'membership_id'
    _order = 'id desc'

    name = fields.Char(string='Name', readonly=True)
    membership_id = fields.Many2one('res.partner', string='Name', required=True, track_visibility="onchange",
                                    domain=[('state', '=', 'member')], readonly=True,
                                    states={'request': [('readonly', False)]})
    request_date = fields.Date(string='Request Date', default=fields.Date.today(), required=True,
                               track_visibility="onchange",
                               readonly=True, states={'request': [('readonly', False)]})

    approve_date = fields.Date(string='Approve Date', default=fields.Date.today(), track_visibility="onchange",
                               readonly=True, states={'request': [('readonly', False)]})
    invoice_id = fields.Many2one('account.invoice', string='Invoice', track_visibility="onchange", readonly=True)
    state = fields.Selection([('request', 'Request'), ('invoice', 'Invoiced'), ('done', 'Done'), ('reject', 'Reject')],
                             default='request', string='State', track_visibility="onchange")

    @api.constrains('membership_id')
    def check_duplicate(self):
        rec = self.search([('membership_id', '=', self.membership_id.id), ('state', 'in', ['request', 'invoice'])])
        if len(rec) > 1:
            raise ValidationError(
                _('Currently a record exist for processing with member'.format(self.membership_id.name)))

    @api.one
    def act_invoice(self):
        if 'request' in self.state:
            invoice_id = self.membership_id._create_invoice()
            sequence = self.env['ir.sequence'].next_by_code('renew.member.request.seq')
            self.write({'name': sequence,
                        'invoice_id': invoice_id.id,
                        'state': 'invoice',
                        })

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
        return [('state', 'in', ['request', 'invoice'])]

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('invoice', 'done', 'reject'):
                raise Warning(_('[Warning] Record cannot deleted.'))
        return super(RenewRequest, self).unlink()
