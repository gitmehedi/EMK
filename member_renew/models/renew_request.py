from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class RenewRequest(models.Model):
    _name = 'renew.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Membership Renew Request'
    _rec_name = 'membership_id'
    _order = 'id desc'

    def _default_renew_amount(self):
        product = self.env['product.product'].search([('membership_status', '=', True)], order='id desc',
                                                     limit=1)
        return product.list_price

    def _default_payment(self):
        partner = self.env['account.payment'].search([('partner_id', '=', self.membership_id.id)])
        return partner

    name = fields.Char(string='Name', readonly=True)
    membership_id = fields.Many2one('res.partner', string='Name', required=True, track_visibility="onchange",
                                    domain=[('state', '=', 'member')], readonly=True,
                                    states={'request': [('readonly', False)]})
    membership_state_date = fields.Date(related='membership_id.membership_last_start', string="Start Date", store=True)
    membership_end_date = fields.Date(related='membership_id.membership_stop', string="End Date", store=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.today(), required=True,
                               track_visibility="onchange", readonly=True, states={'request': [('readonly', False)]})
    payment_ids = fields.Many2many('account.payment', string='Payment')
    payment_amount = fields.Float(string='Payment Amount')
    renew_amount = fields.Float(string="Renew Amount", track_visibility="onchange", required=True,
                                default=_default_renew_amount, readonly=True, states={'request': [('readonly', False)]})
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

    @api.onchange('membership_id')
    def onchange_membership(self):
        res = {}
        payments = self.env['account.payment'].search([('partner_id', '=', self.membership_id.id)])
        pay_ids = [val.id for val in payments if not val.invoice_ids]
        res['domain'] = {
            'payment_ids': [('id', 'in', pay_ids)],
        }
        return res

    @api.onchange('payment_ids')
    def onchange_payment_ids(self):
        if self.payment_ids:
            self.payment_amount = sum([val.amount for val in self.payment_ids])

    @api.one
    def act_invoice(self):
        if 'request' in self.state:
            # invoice_id = self.membership_id._create_invoice()
            sequence = self.env['ir.sequence'].next_by_code('renew.member.request.seq')
            mem_inv = self.env['membership.membership_line'].search([('account_invoice_line', '=', inv_line.id)])
            self.payment_ids.write({'invoice_ids': [(6, 0, [self.invoice_id.id])]})
            self.env['account.payment'].search([('partner_id', '=', self.membership_id.id)])
            mem_inv.write({
                'date': self.date,
                'date_from': self.date,
                # 'date_to': inv_line.product_id.product_tmpl_id._get_next_date(self.date)
            })
            # self.write({'name': sequence,
            #             'invoice_id': invoice_id.id,
            #             'state': 'invoice',
            #             })

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
