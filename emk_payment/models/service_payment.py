# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ServicePayment(models.Model):
    _name = 'service.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'membership_id'
    _order = 'collection_date DESC, id desc'

    @api.model
    def _get_session(self):
        session = self.env['payment.session'].search(
            [('open', '=', True), ('user_id', '=', self.env.user.partner_id.id)])
        if not session:
            raise UserError(_('Session is not opened. Please open a session.'))
        return session

    @api.model
    def default_journal(self):
        journal = self.env['account.journal'].search([('type', 'in', ['cash'])], limit=1)
        if len(journal) > 0:
            return journal

    name = fields.Char()
    paid_amount = fields.Float(string='Payment Amount', compute='_compute_paid_amount', store=True,
                               track_visibility='onchange')
    comments = fields.Text(string='Comments', readonly=True, states={'open': [('readonly', False)]},
                           track_visibility='onchange')
    collection_date = fields.Date(default=fields.Datetime.now, string='Date', required=True, readonly=True,
                                  states={'open': [('readonly', False)]}, track_visibility='onchange')
    membership_id = fields.Many2one('res.partner', string='Payment For',
                                    readonly=True, states={'open': [('readonly', False)]}, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])], default=default_journal,
                                 readonly=True, states={'open': [('readonly', False)]}, track_visibility='onchange')
    session_id = fields.Many2one('payment.session', compute='_compute_session', string="Session Name", store=True,
                                 required=True, default=_get_session)
    event_id = fields.Many2one('event.event', string='Event Name', domain=[('state', '=', 'confirm')])
    event_participant_id = fields.Many2one('event.registration', string='Payment For')
    responsible_id = fields.Many2one('res.partner', default=lambda self: self.env.user.id, string='Responsible',
                                     required=True, readonly=True, track_visibility='onchange')
    payment_type_id = fields.Many2one('product.template', string='Payment Type', required=True,
                                      track_visibility='onchange',
                                      domain=[('type', '=', 'service'), ('purchase_ok', '=', False),
                                              ('sale_ok', '=', False),('service_type', '=', True)],
                                      readonly=True, states={'open': [('readonly', False)]})
    check_type = fields.Char()
    company_id = fields.Many2one('res.company', string='Company Name', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid'), ('cancel', 'Cancel')], default='open', string='State',
                             track_visibility='onchange')

    def _compute_session(self):
        for rec in self:
            rec.session_id = self._get_session()

    @api.onchange('payment_type_id')
    def _onchage_payment_type(self):
        res = {}
        self.membership_id = None
        self.event_id = None
        self.check_type = self.payment_type_id.service_type
        if self.payment_type_id.service_type == 'card':
            member = self.env['member.card.replacement'].search([('state', '=', 'approve')])
            ids = [rec.membership_id.id for rec in member]
            res['domain'] = {
                'membership_id': [('id', 'in', ids)],
            }
        return res

    @api.onchange('event_id')
    def _onchage_event(self):
        res = {}
        self.event_participant_id = None
        if self.event_id == 'card':
            event = self.env['event.registration'].search([('event_id', '=', self.event_id.id), ('active', '=', True)])
            res['domain'] = {
                'event_participant_id': [('id', 'in', event.ids)],
            }
        return res

    @api.depends('payment_type_id', 'event_id')
    def _compute_paid_amount(self):
        for rec in self:
            if rec.payment_type_id.service_type == 'card':
                rec.paid_amount = rec.payment_type_id.list_price
            if rec.payment_type_id.service_type == 'event_fee' and rec.event_id:
                rec.paid_amount = rec.event_id.participating_amount

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.one
    def act_cancel(self):
        if self.state == 'open':
            self.state = 'cancel'

    @api.one
    def act_payment_register(self):
        if self.state == 'open':
            payment = self.env['account.payment']
            if self.state == 'open':
                payment_method_id = self.env['account.payment.method'].search(
                    [('code', '=', 'manual'), ('payment_type', '=', 'inbound')])
                record = {}
                record['payment_type'] = 'inbound'
                record['payment_method_id'] = payment_method_id.id
                record['partner_type'] = 'customer'
                record['partner_id'] = self.membership_id.id
                record['amount'] = self.paid_amount
                record['journal_id'] = self.journal_id.id
                record['payment_date'] = self.collection_date
                record['communication'] = ''
                payment = payment.create(record)
                payment.post()
                if payment:
                    self.state = 'paid'
                    self.name = self.env['ir.sequence'].next_by_code('service.payment.seq')

    @api.multi
    def print_receipt(self):
        self.ensure_one()
        report = self.env['report'].get_action(self, 'emk_payment.service_payment_receipt_tmpl')
        return report
