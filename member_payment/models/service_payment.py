# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, Warning


class ServicePayment(models.Model):
    _name = 'service.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Service Payment'
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

    paid_amount = fields.Float(string='Payment Amount', compute='_compute_paid_amount', store=True,
                               track_visibility="onchange")
    comments = fields.Text(string='Comments', readonly=True, states={'open': [('readonly', False)]},
                           track_visibility="onchange")
    collection_date = fields.Date(default=fields.Datetime.now, string='Date', required=True, readonly=True,
                                  states={'open': [('readonly', False)]}, track_visibility="onchange")
    membership_id = fields.Many2one('res.partner', string='Member Name', required=True,
                                    domain=[('state', '=', 'member')],
                                    readonly=True, states={'open': [('readonly', False)]}, track_visibility="onchange")
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])], default=default_journal,
                                 readonly=True, states={'open': [('readonly', False)]}, track_visibility="onchange")

    session_id = fields.Many2one('payment.session', compute='_compute_session', string="Session Name", store=True,
                                 required=True, default=_get_session, track_visibility="onchange")
    payment_type_id = fields.Many2one('product.template', string='Payment Type', required=True,
                                      domain=[('type', '=', 'service'), ('purchase_ok', '=', False),
                                              ('sale_ok', '=', False)],
                                      readonly=True, states={'open': [('readonly', False)]},
                                      track_visibility="onchange")
    check_type = fields.Char(track_visibility="onchange")
    card_replacement_id = fields.Many2one('member.card.replacement', string='Card Replacement',
                                          domain=[('state', '=', 'approve')], readonly=True,
                                          states={'open': [('readonly', False)]}, track_visibility="onchange")
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid'), ('cancel', 'Cancel')], default='open',
                             string='State', track_visibility="onchange")

    @api.constrains('membership_id')
    def check_duplicate(self):
        rec = self.search([('membership_id', '=', self.membership_id.id), ('state', 'in', ['open'])])
        if len(rec) > 1:
            raise ValidationError(
                _('Currently a record exist for processing with member'.format(self.membership_id.name)))

    def _compute_session(self):
        for rec in self:
            rec.session_id = self._get_session()

    @api.onchange('payment_type_id')
    def _onchage_payment_type(self):
        self.membership_id = False
        self.check_type = self.payment_type_id.service_type
        if self.payment_type_id.service_type != 'card':
            res = {}
            self.card_replacement_id = False
            partner = self.env['res.partner'].search([])
            res['domain'] = {
                'membership_id': [('id', 'in', partner.ids)],
            }
            return res

    @api.onchange('card_replacement_id')
    def _onchage_card_replacement(self):
        if self.card_replacement_id:
            res, ids = {}, []
            self.membership_id = False
            for rec in self.env['member.card.replacement'].search([('state', '=', 'approve')]):
                if rec.membership_id:
                    ids.append(rec.membership_id.id)
            res['domain'] = {
                'membership_id': [('id', 'in', ids)],
            }
            return res

    @api.depends('payment_type_id')
    def _compute_paid_amount(self):
        for rec in self:
            rec.paid_amount = rec.payment_type_id.list_price

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

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('paid', 'cancel'):
                raise Warning(_('[Warning] Paid record cannot deleted.'))
        return super(ServicePayment, self).unlink()
