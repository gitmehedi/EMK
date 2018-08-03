# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MemberPayment(models.Model):
    _name = 'member.payment'
    _rec_name = 'membership_id'
    _order = 'date desc'

    due_amount = fields.Integer(string='Due Amount', store=True,
                                readonly=True, states={'draft': [('readonly', False)]})
    paid_amount = fields.Integer(string='Paid Amount', required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    payment_ref = fields.Text(string='Payment Ref', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(default=fields.Datetime.now(), string='Date', readonly=True,
                       states={'draft': [('readonly', False)]})

    membership_id = fields.Many2one('res.partner', string='Applicant/Member', required=True,
                                    domain=['&', ('is_applicant', '=', True), ('credit', '>', 0)],
                                    readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])],
                                 readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft', string='State')

    @api.onchange('membership_id')
    def onchange_membership(self):
        if self.membership_id:
            self.due_amount = self.membership_id.credit
            self.paid_amount = self.membership_id.credit

    @api.one
    def member_payment(self):
        invoice = self.env['account.invoice'].search(
            [('partner_id', '=', self.membership_id.id), ('state', '=', 'open')],
            order='create_date desc')
        pay_text = 'PAID for Membership'
        rem_amount = self.paid_amount

        if 'draft' in self.state and invoice:
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

                if inv_amount > 0:
                    record = {}
                    record['payment_type'] = 'inbound'
                    record['payment_method_id'] = payment_method_id.id
                    record['partner_type'] = 'customer'
                    record['invoice_ids'] = [(6, 0, [rec.id])]
                    record['partner_id'] = self.membership_id.id
                    record['amount'] = inv_amount
                    record['journal_id'] = rec.journal_id.id
                    record['payment_date'] = self.date
                    record['communication'] = pay_text
                    payment = rec.payment_ids.create(record)
                    payment.post()

                    if payment and len(payment_ref) > 0:
                        payment_ref = payment_ref + ', ', invoice.display_name
                    else:
                        payment_ref = invoice.display_name

                    if not rem_amount:
                        self.state = 'paid'
                        self.payment_ref = payment_ref

                    if invoice.state and self.membership_id.state == 'invoice':
                        seq = self.env['ir.sequence'].next_by_code('res.partner.member')
                        self.membership_id.write({'state': 'member', 'member_sequence': seq,
                                                  'application_ref': self.membership_id.member_sequence})

                    return True
