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

    @api.multi
    def get_all_unreconciled_credit_entries(self):
        for rec in self:
            ids = []

            move_lines = rec.env['account.move.line'].search([('reconciled','=',True),
                                                              ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                                                              ('date', '>=', self.date),
                                                              ('partner_id', '=', self.partner_id.id),
                                                              ('is_clearing_journal_entry','=',False),
                                                              ('credit','>=',self.amount)
                                                              ])

            # Account Module - account_view.xml 

            # < filter
            # string = "Unreconciled"
            # domain = "[('full_reconcile_id', '=', False), ('balance','!=', 0), ('account_id.reconcile','=',True)]"
            # help = "Journal items where matching number isn't set"
            # name = "unreconciled" / >

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

