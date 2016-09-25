# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv
from openerp.report import report_sxw
from common_report_header import common_report_header


class inherited_journal_print(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(journal_print, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.period_ids = []
        self.streamline = False
        self.last_move_id = False
        self.journal_ids = []
        self.sort_selection = 'am.name'
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'display_currency':self._display_currency,
            'get_sortby': self._get_sortby,
            'get_target_move': self._get_target_move,
            'check_last_move_id': self.check_last_move_id,
            'set_last_move_id': self.set_last_move_id,
            'tax_codes': self.tax_codes,
            'sum_vat': self._sum_vat,
    })

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        new_ids = ids
        self.query_get_clause = ''
        self.target_move = data['form'].get('target_move', 'all')
        if data['form']['used_context']['a1_id']:
            self.streamline = data['form']['used_context']['a1_id'][0]
        if (data['model'] == 'ir.ui.menu'):
            self.period_ids = tuple(data['form']['periods'])
            self.journal_ids = tuple(data['form']['journal_ids'])
            new_ids = data['form'].get('active_ids', [])
            self.query_get_clause = 'AND '
#             self.query_get_clause += obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
            self.query_get_clause += obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
#             self.query_get_clause += obj_move._query_get(self.cr, self.uid, obj='l', context=data['form']['used_context']['a1_id'][0])
            self.sort_selection = data['form'].get('sort_selection', 'date')
#             print "selfselfself",self.query_get_clause
            objects = self.pool.get('account.journal.period').browse(self.cr, self.uid, new_ids)
        elif new_ids:
            #in case of direct access from account.journal.period object, we need to set the journal_ids and periods_ids
            self.cr.execute('SELECT period_id, journal_id FROM account_journal_period WHERE id IN %s', (tuple(new_ids),))
            res = self.cr.fetchall()
            self.period_ids, self.journal_ids = zip(*res)
        return super(journal_print, self).set_context(objects, data, ids, report_type=report_type)


