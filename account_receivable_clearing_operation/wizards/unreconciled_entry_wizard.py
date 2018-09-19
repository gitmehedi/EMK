from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import time, datetime


class UnReconciledJournalEntryWizard(models.TransientModel):
    _name = 'unreconciled.journal.entry.wizard'

    date = fields.Date(string='Date')
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])
    ref = fields.Char(string='Ref')
    fiscal_month = fields.Many2one('date.range.type', string='Fiscal Month')
    amount = fields.Float(string='Amount')

    # [action] = self.env.ref('account.action_account_moves_all_a').read()
    # ids = []
    # for aml in self:
    #     if aml.account_id.reconcile:
    #         ids.extend(
    #             [r.debit_move_id.id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id.id for
    #                                                                                         r in
    #                                                                                         aml.matched_credit_ids])
    #         ids.append(aml.id)
    # action['domain'] = [('id', 'in', ids)]
    # return action
    #

    @api.multi
    def get_all_unreconciled_credit_entries(self):
        for rec in self:
            ids = []

            move_lines = rec.env['account.move.line'].search([('reconciled','=',False),
                                                              ('date', '=', self.date),
                                                              ('partner_id', '=', self.partner_id.id),
                                                              ])
            if move_lines:
                for mv_line in move_lines:
                    ids.append(mv_line.id)

            view = self.env.ref('account_receivable_clearing_operation.unreconciled_acc_move_line_tree')



            return {
                'name': ('Unreconcile Journal Entries'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'account.move.line',
                'domain': [('id', 'in', ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }

