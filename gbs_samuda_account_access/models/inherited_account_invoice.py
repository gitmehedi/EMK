import json
from odoo import fields, models, api, _


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_can_view_button(self):
        for rec in self:
            if self.env.user.has_group('gbs_samuda_account_access.group_account_reconciliation_button'):
                rec.can_view_payment_button = True
            else:
                rec.can_view_payment_button = False

    can_view_payment_button = fields.Boolean(string='Can View Button', compute='_compute_can_view_button')

    @api.one
    def _get_outstanding_info_JSON(self):
        super(InheritedAccountInvoice, self)._get_outstanding_info_JSON()
        if json.loads(self.outstanding_credits_debits_widget):
            info = json.loads(self.outstanding_credits_debits_widget)
            info['can_view_payment_button'] = self.can_view_payment_button
            info['type'] = self.type

            indexes = []
            for idx, content in enumerate(info['content']):
                if 'id' in content:
                    journal_id = content['id']
                    account_move_line = self.env['account.move.line'].browse(journal_id)
                    if account_move_line.journal_id.type == 'situation':
                        indexes.append(idx)

            if len(indexes) > 0:
                for index in indexes:
                    del info['content'][index]
            self.outstanding_credits_debits_widget = json.dumps(info)

    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payment_info_JSON(self):
        super(InheritedAccountInvoice, self)._get_payment_info_JSON()
        if json.loads(self.payments_widget):
            info = json.loads(self.payments_widget)
            info['can_view_payment_button'] = self.can_view_payment_button
            self.payments_widget = json.dumps(info)