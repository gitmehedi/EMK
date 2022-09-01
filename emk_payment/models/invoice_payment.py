# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.exceptions import UserError


class MemberPayment(models.Model):
    _name = 'invoice.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _rec_name = 'invoice_id'
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

    invoice_type = fields.Selection([('membership_payment', 'Membership Payment'), ('event_payment', 'Event Payment')],
                                    string="Invoice Type", required=True, readonly=True, track_visibility='onchange',
                                    states={'open': [('readonly', False)]})
    due_amount = fields.Float(string='Due Amount', compute='_compute_due_amount', store=True,
                              track_visibility='onchange')
    paid_amount = fields.Float(string='Paid Amount', required=True, track_visibility='onchange',
                               readonly=True, states={'open': [('readonly', False)]})
    payment_ref = fields.Text(string='Payment Ref', readonly=True, states={'open': [('readonly', False)]},
                              track_visibility='onchange')
    date = fields.Date(default=fields.Datetime.now, string='Payment Date', readonly=True, required=True,
                       states={'open': [('readonly', False)]}, track_visibility='onchange', )
    payment_partner_id = fields.Many2one('res.partner', string='Payment Authority', required=True,
                                         track_visibility='onchange',
                                         readonly=True, states={'open': [('readonly', False)]})
    invoice_id = fields.Many2one('account.invoice', string='Invoice', required=True, track_visibility='onchange',
                                 readonly=True, states={'open': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, track_visibility='onchange',
                                 domain=[('type', 'in', ['bank', 'cash'])], default=default_journal,
                                 readonly=True, states={'open': [('readonly', False)]})
    session_id = fields.Many2one('payment.session', compute='_compute_session', string="Session Name", store=True,
                                 required=True, default=_get_session, track_visibility='onchange')
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid')], default='open', string='State',
                             track_visibility='onchange')

    @api.onchange('invoice_type')
    def onchange_invoice_type(self):
        res = {}
        users = []
        self.payment_partner_id = None
        if self.invoice_type == 'membership_payment':
            inv = self.env['account.invoice'].sudo().search([('state', '=', 'open'),
                                                             ('residual', '>', 0)])
            member_inv = [val.partner_id.id for val in inv]
            members = self.env['res.partner'].sudo().search([('is_applicant', '=', True), ('id', 'in', member_inv)])
            users = members.ids
        if self.invoice_type == 'event_payment':
            payment_users = self.env['account.invoice'].sudo().search(
                [('state', '=', 'open'), ('partner_id.is_poc', '=', True)])
            users = list(set([val.partner_id.id for val in payment_users]))

        res['domain'] = {
            'payment_partner_id': [('id', 'in', users)],
        }
        return res

    @api.onchange('payment_partner_id')
    def onchange_partner(self):
        if self.payment_partner_id:
            res = {}
            self.invoice_id = None
            invoice = self.env['account.invoice'].sudo().search([('state', '=', 'open'),
                                                          ('partner_id', '=', self.payment_partner_id.id),
                                                          ('residual', '>', 0)])
            res['domain'] = {
                'invoice_id': [('id', 'in', invoice.ids)],
            }
            return res

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.invoice_id:
            self.due_amount = self.invoice_id.residual
            self.paid_amount = self.invoice_id.residual

    @api.depends('payment_partner_id')
    def _compute_due_amount(self):
        if self.payment_partner_id:
            self.due_amount = self.invoice_id.residual

    def _compute_session(self):
        for rec in self:
            rec.session_id = self._get_session()

    @api.one
    def invoice_payment(self):
        if self.state != 'open':
            raise UserError(_('You are not in valid state.'))
        vals = {}
        invoice = self.invoice_id

        if self.invoice_type == 'event_payment':
            vals['communication'] = 'Event payment against invoice'
            vals['paid_amount'] = self.paid_amount
            vals['invoice'] = self.invoice_id
            payment = self.create_payment(vals)
            if payment:
                self.state = 'paid'
                if self.invoice_id.move_id:
                    sql = "UPDATE account_invoice SET state='paid' WHERE id={0};".format(self.invoice_id.id)
                    self.env.cr.execute(sql)

        if self.invoice_type == 'membership_payment':
            # invoice = self.env['account.invoice'].search(
            #     [('partner_id', '=', self.payment_partner_id.id), ('state', '=', 'open')],
            #     order='create_date desc')
            vals['communication'] = 'Membership fee payment against invoice'
            vals['paid_amount'] = self.paid_amount
            vals['invoice'] = self.invoice_id
            rem_amount = self.paid_amount

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
                    member = self.payment_partner_id
                    vals['paid_amount'] = inv_amount
                    payment = self.create_payment(vals)

                    if payment and len(payment_ref) > 0:
                        self.payment_ref = payment_ref + ', ' + str(rec.display_name)
                    else:
                        self.payment_ref = str(rec.display_name)

                    if rec.state == 'open' and member.state == 'invoice':
                        membership_state = 'paid' if inv_amount > 0 else 'free'
                        member.write({'state': 'member',
                                      'member_sequence': '',
                                      'application_ref': member.member_sequence,
                                      'free_member': True,
                                      'membership_status': 'active',
                                      'membership_state': membership_state
                                      })
                        for inv_line in invoice.invoice_line_ids:
                            mem_inv = self.env['membership.membership_line'].search(
                                [('account_invoice_line', '=', inv_line.id)])
                            if len(mem_inv) > 0:
                                mem_inv.write({
                                    'date': self.date,
                                    'date_from': self.date,
                                    'date_to': inv_line.product_id.product_tmpl_id._get_next_date(self.date)
                                })

                        rm_grp = self.env['res.groups'].sudo().search(
                            [('name', '=', 'Applicants'), ('category_id.name', '=', 'Membership')])
                        rm_grp.write({'users': [(3, member.user_ids.id)]})
                        add_grp = self.env['res.groups'].sudo().search(
                            [('name', '=', 'Membership User'), ('category_id.name', '=', 'Membership')])
                        add_grp.write({'users': [(4, member.user_ids.id)]})

                        vals = {
                            'template': 'emk_payment.member_payment_confirmation_tmpl',
                            'email_to': member.email,
                            'context': {'name': member.name},
                        }
                        renew_req = self.env['renew.request'].search([('invoice_id', '=', invoice.id)])
                        if renew_req:
                            renew_req.write({'state': 'done'})
                        else:
                            self.env['rfid.generation'].create({'membership_id': member.id})
                        self.env['res.partner'].mailsend(vals)

                    if rec.state == 'open' and member.state == 'member':
                        renew_obj = self.env['renew.request'].search([('invoice_id', '=', invoice.id)])

                        for inv_line in invoice.invoice_line_ids:
                            mem_inv = self.env['membership.membership_line'].search(
                                [('account_invoice_line', '=', inv_line.id)])
                            if len(mem_inv) > 0 and renew_obj:
                                mem_inv.write({
                                    'date': self.date,
                                    'date_from': renew_obj.membership_state_date,
                                    'date_to': renew_obj.membership_end_date
                                })

                        if renew_obj:
                            renew_obj.write({'state': 'done'})

                        vals = {
                            'template': 'emk_payment.member_payment_confirmation_tmpl',
                            'email_to': member.email,
                            'context': {'name': member.name},
                        }

                        self.env['res.partner'].mailsend(vals)

            if rem_amount > 0:
                vals['paid_amount'] = rem_amount
                vals['communication'] = 'Membership fee payment against invoice'
                vals['rem_amount'] = self.paid_amount
                self.create_payment(vals)
                rem_amount = 0

            if not rem_amount:
                self.state = 'paid'
                if self.invoice_id.move_id:
                    sql = "UPDATE account_invoice SET state='paid' WHERE id={0};".format(self.invoice_id.id)
                    self.env.cr.execute(sql)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.one
    def name_get(self):
        name = self.payment_partner_id.name
        if self.payment_partner_id:
            name = '[%s] %s' % (self.payment_partner_id.member_sequence, self.payment_partner_id.name)
        return self.id, name

    def create_payment(self, vals):
        payment_method = self.env['account.payment.method'].search(
            [('code', '=', 'manual'), ('payment_type', '=', 'inbound')])
        payment = {
            'payment_type': 'inbound',
            'payment_method_id': payment_method.id,
            'partner_type': 'customer',
            'partner_id': self.payment_partner_id.id,
            'amount': vals['paid_amount'],
            'journal_id': self.journal_id.id,
            'payment_date': self.date,
            'communication': vals['communication'],
            'invoice_ids': [(6, 0, [vals['invoice'].id])] if 'invoice' in vals else [],
        }

        payment = self.env['account.payment'].create(payment)
        payment.post()
        return payment
