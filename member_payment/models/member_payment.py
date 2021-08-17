# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.exceptions import ValidationError, UserError, Warning


class MemberPayment(models.Model):
    _name = 'member.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Member Fee Payment'
    _order = 'id desc'

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

    due_amount = fields.Float(string='Due Amount', compute='_compute_due_amount', store=True,
                              track_visibility="onchange")
    paid_amount = fields.Float(string='Paid Amount', required=True,
                               readonly=True, states={'open': [('readonly', False)]}, track_visibility="onchange")
    payment_ref = fields.Text(string='Payment Ref', readonly=True, states={'open': [('readonly', False)]},
                              track_visibility="onchange")
    date = fields.Date(default=fields.Datetime.now, string='Payment Date', readonly=True,
                       states={'open': [('readonly', False)]}, track_visibility="onchange")
    membership_id = fields.Many2one('res.partner', string='Applicant/Member', required=True,
                                    domain=['|', ('is_applicant', '=', True), ('credit', '>', 0)],
                                    readonly=True, states={'open': [('readonly', False)]}, track_visibility="onchange")
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])], default=default_journal,
                                 readonly=True, states={'open': [('readonly', False)]}, track_visibility="onchange")

    session_id = fields.Many2one('payment.session', compute='_compute_session', string="Session Name", store=True,
                                 required=True, default=_get_session, track_visibility="onchange")
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid')], default='open', string='State',
                             track_visibility="onchange")

    @api.constrains('membership_id')
    def check_duplicate(self):
        rec = self.search([('membership_id', '=', self.membership_id.id), ('state', 'in', ['open'])])
        if len(rec) > 1:
            raise ValidationError(
                _('Currently a record exist for processing with member'.format(self.membership_id.name)))

    @api.onchange('membership_id')
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
        if self.state != 'open':
            raise UserError(_('You are not in valid state.'))
        if not self.membership_id.user_ids:
            raise ValidationError(
                _("This user does not have any access credentials. Please create it first."))

        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.membership_id.id), ('state', '=', 'open')],
            order='create_date desc')
        pay_text = 'Payment for Membership'
        rem_amount = self.paid_amount
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
                    'journal_id': self.journal_id.id,
                    'payment_date': self.date,
                    'communication': pay_text,
                })
                payment.post()

                if payment and len(payment_ref) > 0:
                    self.payment_ref = payment_ref + ', ' + str(rec.display_name)
                else:
                    self.payment_ref = str(rec.display_name)

                if rec.state == 'paid' and self.membership_id.state == 'invoice':
                    membership_state = 'paid' if inv_amount > 0 else 'free'
                    self.membership_id.write({'state': 'member',
                                              'application_ref': self.membership_id.member_sequence,
                                              'free_member': True,
                                              'membership_status': 'active',
                                              'membership_state': membership_state
                                              })
                    for inv_line in invoice.invoice_line_ids:
                        mem_inv = self.env['membership.membership_line'].search([
                            ('account_invoice_line', '=', inv_line.id)])
                        if len(mem_inv) > 0:
                            mem_inv.write({
                                'date': self.date,
                                'date_from': self.date,
                                'date_to': inv_line.product_id.product_tmpl_id._get_next_date(self.date)
                            })

                    rm_grp = self.env['res.groups'].sudo().search(
                        [('name', '=', 'Applicants'), ('category_id.name', '=', 'Membership')])
                    rm_grp.write({'users': [(3, self.membership_id.user_ids.id)]})
                    add_grp = self.env['res.groups'].sudo().search(
                        [('name', '=', 'Membership User'), ('category_id.name', '=', 'Membership')])
                    add_grp.write({'users': [(4, self.membership_id.user_ids.id)]})

                    vals = {
                        'template': 'member_payment.member_payment_confirmation_tmpl',
                        'email_to': self.membership_id.email,
                        'context': {'name': self.membership_id.name},
                    }
                    renew_req = self.env['renew.request'].search([('invoice_id', '=', invoice.id)])
                    if renew_req:
                        renew_req.write({'state': 'done'})
                    else:
                        self.env['rfid.generation'].create({'membership_id': self.membership_id.id})
                    self.env['res.partner'].mailsend(vals)

        if rem_amount > 0:
            payment = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'payment_method_id': payment_method_id.id,
                'partner_type': 'customer',
                'partner_id': self.membership_id.id,
                'amount': rem_amount,
                'journal_id': self.journal_id.id,
                'payment_date': self.date,
                'communication': pay_text,
            })
            payment.post()
            rem_amount = 0

        if not rem_amount:
            self.state = 'paid'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.one
    def name_get(self):
        name = self.membership_id.name
        if self.membership_id:
            name = '[%s] %s' % (self.membership_id.member_sequence, self.membership_id.name)
        return (self.id, name)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('paid',):
                raise Warning(_('[Warning] Paid record cannot deleted.'))
        return super(MemberPayment, self).unlink()
