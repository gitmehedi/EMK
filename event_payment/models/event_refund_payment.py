# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.exceptions import ValidationError, UserError


class EventRefundPayment(models.Model):
    _name = 'event.refund.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _rec_name = 'payment_partner_id'
    _description = 'Invoice Payment'

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

    event_id = fields.Many2one('event.event', string="Event", required=True, readonly=True,
                               states={'open': [('readonly', False)]}, track_visibility='onchange')
    invoice_id = fields.Many2one('account.invoice', string="Refund Invoice", required=True, store=True,
                                 track_visibility='onchange')
    ref_invoice_id = fields.Many2one('account.invoice', string="Invoice", track_visibility='onchange')
    paid_amount = fields.Float(string='Paid Amount', digits=(11, 2), required=True)
    payment_ref = fields.Text(string='Payment Ref', readonly=True, states={'open': [('readonly', False)]},
                              track_visibility='onchange')
    date = fields.Date(default=fields.Datetime.now, string='Payment Date', readonly=True, required=True,
                       states={'open': [('readonly', False)]}, track_visibility='onchange')
    payment_partner_id = fields.Many2one('res.partner', string='Payment Authority', required=True, store=True,
                                         domain=[('is_organizer', '=', 'True')], track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])], default=default_journal,
                                 readonly=True, states={'open': [('readonly', False)]}, track_visibility='onchange')
    session_id = fields.Many2one('payment.session', compute='_compute_session', string="Session Name", store=True,
                                 required=True, default=_get_session, track_visibility='onchange')
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid')], default='open', string='State',
                             track_visibility='onchange')

    @api.onchange('event_id')
    def onchange_event(self):
        self.paid_amount = None
        self.invoice_id = None
        self.payment_partner_id = None
        if self.event_id:
            reserv = self.env['event.reservation'].search([('event_id', '=', self.event_id.id)])
            inv = self.env['account.invoice'].search([('origin', '=', reserv.name), ('state', '=', 'paid'),
                                                      ('amount_total', '=', self.event_id.refundable_amount)])
            if inv:
                self.invoice_id = inv.id
                self.payment_partner_id = self.event_id.organizer_id.id
                self.paid_amount = self.event_id.refundable_amount

    def _compute_session(self):
        for rec in self:
            rec.session_id = self._get_session()

    @api.one
    def invoice_payment(self):
        if self.state != 'open':
            raise UserError(_('You are not in valid state.'))

        ref_inv = self.env['account.invoice.refund'].with_context(
            active_ids=[self.invoice_id.id]).create({'filter_refund': 'refund',
                                                     'description': 'Refund created',
                                                     }).invoice_refund()
        inv = self.invoice_id.search(ref_inv['domain'])
        if inv:
            inv.action_invoice_open()
            # inv.write({'reconciled': 'False'})
            # self.ref_invoice_id = inv.id
            #
            # payment_method = self.env['account.payment.method'].search(
            #     [('code', '=', 'manual'), ('payment_type', '=', 'inbound')])
            #
            # payment = self.env['account.payment'].create({
            #     'payment_type': 'inbound',
            #     'payment_method_id': payment_method.id,
            #     'partner_type': 'customer',
            #     'partner_id': inv.partner_id.id,
            #     'amount': inv.amount_total,
            #     'journal_id': inv.journal_id.id,
            #     'payment_date': inv.date_invoice,
            #     'communication': inv.name,
            #     'invoice_ids': [(6, 0, [inv.id])],
            # })
            # payment.post()
            #
            # if payment:
            #     self.state = 'paid'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.one
    def name_get(self):
        name = self.payment_partner_id.name
        if self.payment_partner_id:
            name = '[%s] %s' % (self.payment_partner_id.member_sequence, self.payment_partner_id.name)
        return (self.id, name)
