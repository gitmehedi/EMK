# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PaymentSession(models.Model):
    _name = 'payment.session'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'start_at desc'

    @api.model
    def get_default_user(self):
        return self.env.user.partner_id

    name = fields.Char(string='Name')
    start_at = fields.Date(default=fields.Datetime.now(), string='Opening Date', required=True, readonly=True)
    stop_at = fields.Date(string='Closing Date', readonly=True, states={'draft': [('readonly', False)]})
    total_amount = fields.Float(string="Total Amount", digits=(10, 2), compute="_compute_total_amount")

    member_fee_ids = fields.One2many('member.payment', 'session_id', string='Membership Fee')
    service_fee_ids = fields.One2many('service.payment', 'session_id', string='Service Fee')
    user_id = fields.Many2one('res.partner', string='Responsible', required=True, default=get_default_user)
    open = fields.Boolean(default=True)

    state = fields.Selection(
        [('opening_control', 'Opening Control'), ('opened', 'Opened'), ('closing_control', 'Closing Control'),
         ('closed', 'Closed')], default='opening_control', string='State')

    @api.depends('member_fee_ids', 'service_fee_ids')
    def _compute_total_amount(self):
        for rec in self:
            return 10

    @api.model
    def create(self, vals):
        if vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.session.seq')
        return super(PaymentSession, self).create(vals)

    @api.constrains('name')
    def unique_session(self):
        vals = self.search([('open', '=', True)])
        if len(vals) > 1:
            raise ValueError(_('Session already Open. Please close session before open another.'))
