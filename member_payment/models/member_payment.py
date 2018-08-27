# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.exceptions import ValidationError, UserError


class MemberPayment(models.Model):
    _name = 'member.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    @api.model
    def _get_session(self):
        session = self.env['payment.session'].search([('open', '=', True)])
        if not session:
            raise UserError(_('Session is not opened. Please open a session.'))
        return session

    due_amount = fields.Float(string='Due Amount', compute='_compute_due_amount', store=True)
    paid_amount = fields.Float(string='Paid Amount', required=True,
                               readonly=True, states={'open': [('readonly', False)]})
    payment_ref = fields.Text(string='Payment Ref', readonly=True, states={'open': [('readonly', False)]})
    date = fields.Date(default=fields.Datetime.now(), string='Payment Date', readonly=True,
                       states={'open': [('readonly', False)]})
    membership_id = fields.Many2one('res.partner', string='Applicant/Member', required=True,
                                    domain=['&', ('is_applicant', '=', True), ('credit', '>', 0)],
                                    readonly=True, states={'open': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])],
                                 readonly=True, states={'open': [('readonly', False)]})

    session_id = fields.Many2one('payment.session', compute='_compute_session', string="Session Name", store=True,
                                 required=True, default=_get_session)
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid')], default='open', string='State')

    def onchange_membership(self):
        if self.membership_id:
            self.due_amount = self.membership_id.credit
            self.paid_amount = self.membership_id.credit

    @api.depends('membership_id')
    def _compute_due_amount(self):
        if self.membership_id:
            self.due_amount = self.membership_id.credit

    def _compute_session(self):
        for rec in self:
            rec.session_id = self._get_session()

    @api.one
    def member_payment(self):
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.membership_id.id), ('state', '=', 'open')],
            order='create_date desc')
        pay_text = 'Payment for Membership'
        rem_amount = self.paid_amount

        if self.state == 'open' and invoice:
            payment_method_id = self.env['account.payment.method'].search(
                [('code', '=', 'manual'), ('payment_type', '=', 'inbound')])
            payment_ref = ''
            for rec in invoice:
                if rem_amount > rec.residual:
                    rem_amount = rem_amount - rec.residual
                    inv_amount = rec.residual
                else:
                    inv_amount = rem_amount
                    rem_amount = 0

                if not inv_amount:
                    raise UserError(_('Paid amount should have a value.'))

                if inv_amount > 0:
                    payment = rec.payment_ids.create({
                        'payment_type': 'inbound',
                        'payment_method_id': payment_method_id.id,
                        'partner_type': 'customer',
                        'invoice_ids': [(6, 0, [rec.id])],
                        'partner_id': self.membership_id.id,
                        'amount': inv_amount,
                        'journal_id': rec.journal_id.id,
                        'payment_date': self.date,
                        'communication': pay_text,
                    })
                    payment.post()

                    if payment and len(payment_ref) > 0:
                        payment_ref = payment_ref + ', ' + str(rec.display_name)
                    else:
                        payment_ref = str(rec.display_name)

                    if not rem_amount:
                        self.state = 'paid'
                        self.payment_ref = payment_ref

                    if rec.state and self.membership_id.state == 'invoice':
                        seq = self.env['ir.sequence'].next_by_code('res.partner.member')
                        self.membership_id.write({'state': 'member',
                                                  'member_sequence': seq,
                                                  'application_ref': self.membership_id.member_sequence,
                                                  'free_member': self.membership_id.member_sequence,
                                                  'membership_state': 'free'
                                                  })
                        for inv_line in invoice.invoice_line_ids:
                            mem_inv = self.env['membership.membership_line'].search([
                                ('account_invoice_line', '=', inv_line.id)])
                            if mem_inv:
                                self.env['membership.membership_line'].write({
                                    'date': mem_inv.membership_id.membership_date_from,
                                    'date_from': mem_inv.membership_id.membership_date_from,
                                    'date_to': mem_inv.membership_id.membership_date_to})

                        vals = {
                            'template': 'member_payment.member_payment_confirmation_tmpl',
                            'email': self.membership_id.email,
                            'email_to': self.membership_id.email,
                            'attachment_ids': '',
                            'context': {},
                        }

                        self.env['res.partner'].mailsend(vals)
                        self.env['rfid.generation'].create({'membership_id': self.membership_id.id})

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.one
    def name_get(self):
        name = self.membership_id.name
        if self.membership_id:
            name = '[%s] %s' % (self.membership_id.member_sequence, self.membership_id.name)
        return (self.id, name)
