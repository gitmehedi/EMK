from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import time, datetime


class UnReconciledJournalEntryWizard(models.TransientModel):
    _name = 'unreconciled.journal.entry.wizard'

    date = fields.Date(string='Date')
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])
    amount = fields.Float(string='Amount')

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    company_id = fields.Many2one(comodel_name='res.company', string='Company', index=1,default=_default_company)

    date_range_fm_id = fields.Many2one(
        comodel_name='date.range', string="Fiscal month",
        compute='_compute_date_range_fm', search='_search_date_range_fm')


    @api.multi
    @api.depends('date', 'company_id')
    def _compute_date_range_fm(self):
        for rec in self:
            date = rec.date
            company = rec.company_id
            rec.date_range_fm_id = company.find_daterange_fm(date)




    @api.multi
    def get_all_unreconciled_credit_entries(self):
        for rec in self:
            ids = []

            move_lines = rec.env['account.move.line'].search([('reconciled', '=', False),
                                                              ('full_reconcile_id', '=', False),
                                                              ('date', '>=', self.date),
                                                              ('partner_id', '=', self.partner_id.id),
                                                              ('is_clearing_journal_entry', '=', False),
                                                              ('credit', '>', self.amount),
                                                              ('date_range_fm_id','=',self.date_range_fm_id.id)
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
