# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MemberPayment(models.Model):
    _name = 'member.payment'
    _rec_name = 'membership_id'

    due_amount = fields.Integer(string='Due Amount', required=True)
    paid_amount = fields.Integer(string='Paid Amount', required=True)
    payment_ref = fields.Char(string='Payment Ref')
    date = fields.Date(default=fields.Datetime.now(), string='Date')

    membership_id = fields.Many2one('res.partner', string='Applicant/Member', required=True,
                                    domain=['&', ('is_applicant', '=', True), ('credit', '>', 0)])
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, default=False)

    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft', string='State')

    @api.onchange('membership_id')
    def onchange_membership(self):
        if self.membership_id:
            self.due_amount = self.membership_id.credit
            self.paid_amount = self.membership_id.credit

    @api.one
    def member_payment(self):
        if 'draft' in self.state:
            if self.paid_amount > 0:
                lines = []
                pay_text = 'PAID for Membership'
                invoice = self.env['account.invoice'].search(
                    [('partner_id', '=', self.membership_id.id), ('state', '=', 'open')],
                    order='create_date desc', limit=1)
                move = self.env['account.move.line'].search(
                    [('credit', '=', '0'), ('move_id', '=', invoice.move_id.id)])

                payment = {}
                payment['account_id'] = move.account_id.id
                payment['partner_id'] = self.membership_id.id
                payment['credit'] = invoice.invoice_line_ids.price_unit
                payment['name'] = pay_text
                payment['narration'] = pay_text

                lines.append((0, 0, payment))

                for rec in invoice.move_id.line_ids:
                    record = {}
                    record['payment_journal'] = rec.account_id.id
                    record['partner_id'] = self.membership_id.id
                    record['debit'] = rec.debit
                    record['name'] = pay_text
                    record['narration'] = invoice.move_id.name
                    lines.append((0, 0, record))

                journal_id = self.env['account.journal'].search([('code', '=', 'BNK1')])
                payment_method = self.env['account.payment.method'].search(
                    [('code', '=ilike', 'manual'), ('payment_type', '=', 'inbound')])
                move_line = {
                    'journal_id': journal_id.id,
                    'ref': pay_text,
                    'narration': pay_text,
                    'payment_method_id': payment_method.id,
                    'payment_type': 'inbound',
                    'amount': self.paid_amount,
                    'partner_type': 'customer',
                    'partner_id': self.membership_id.id,
                    'line_ids': lines
                }
                payment = self.env['account.payment'].create(move_line)
                payment.post()
                if payment:
                    self.state = 'paid'

                if self.membership_id.state == 'member':
                    seq = self.env['ir.sequence'].next_by_code('res.partner.member')
                    self.membership_id.write({'state': 'member', 'member_sequence': seq})

            return True
