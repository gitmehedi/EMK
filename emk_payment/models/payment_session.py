# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PaymentSession(models.Model):
    _name = 'payment.session'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Payment Session"
    _order = 'id desc'

    @api.model
    def get_default_user(self):
        return self.env.user.partner_id

    name = fields.Char(string='Name', track_visibility="onchange")
    start_at = fields.Datetime(default=fields.Datetime.now, string='Opening Date', required=True, readonly=True,
                               track_visibility="onchange")
    stop_at = fields.Datetime(string='Closing Date', readonly=True, states={'draft': [('readonly', False)]},
                              track_visibility="onchange")
    total_amount = fields.Float(string="Total Amount", digits=(10, 2), compute="_compute_total_amount",
                                track_visibility="onchange")
    invoice_payment_ids = fields.One2many('invoice.payment', 'session_id', domain=[('state', 'in', ['draft', 'paid'])],
                                     string='Membership Fee', track_visibility="onchange")
    service_fee_ids = fields.One2many('service.payment', 'session_id', domain=[('state', 'in', ['draft', 'paid'])],
                                      string='Service Fee', track_visibility="onchange")
    user_id = fields.Many2one('res.partner', string='Responsible', required=True, default=get_default_user,
                              track_visibility="onchange")
    open = fields.Boolean(default=True, track_visibility="onchange")

    state = fields.Selection([('opened', 'Opened'), ('validate', 'Validate'), ('closed', 'Closed')], default='opened',
                             string='State', track_visibility="onchange")

    @api.depends('invoice_payment_ids', 'service_fee_ids')
    def _compute_total_amount(self):
        for rec in self:
            inv_coll = sum([val.paid_amount for val in rec.invoice_payment_ids])
            ser_coll = sum([val.paid_amount for val in rec.service_fee_ids])
            rec.total_amount = inv_coll + ser_coll

    @api.model
    def create(self, vals):
        if vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.session.seq')
        return super(PaymentSession, self).create(vals)

    @api.constrains('name')
    def unique_session(self):
        vals = self.search([('open', '=', True), ('user_id', '=', self.user_id.id)])
        if len(vals) > 1:
            raise UserError(_('Session already open. Please close session before open another.'))

    @api.one
    def act_open(self):
        if self.state == 'validate':
            self.state = 'opened'

    @api.one
    def act_validate(self):
        if self.state == 'opened':
            mstates, sstates = 0, 0

            for rec in self.member_fee_ids:
                if rec.state == 'open':
                    mstates = mstates + 1
            for rec in self.service_fee_ids:
                if rec.state == 'open':
                    sstates = sstates + 1
            if mstates > 0:
                raise UserError(_('Membership payment not posting properly.'))
            if sstates > 0:
                raise UserError(_('Service payment not posting properly.'))
            self.state = 'validate'

    @api.one
    def act_close(self):
        if self.state == 'validate':
            self.open = False
            self.stop_at = fields.Datetime.now()
            self.state = 'closed'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'opened')]
