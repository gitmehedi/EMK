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
from datetime import datetime

from openerp import workflow
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.report import report_sxw
import openerp
from dns.rdatatype import NULL

class inherited_account_move_line(osv.osv):
    _inherit = "account.move.line"
    _description = "Journal Items"

    def _query_get(self, cr, uid, obj='l', context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        fiscalyear_ids = []
        context = dict(context or {})
        initial_bal = context.get('initial_bal', False)
        company_clause = " "
        query = ''
        query_params = {}
        if context.get('company_id'):
            company_clause = " AND " +obj+".company_id = %(company_id)s"
            query_params['company_id'] = context['company_id']
        if not context.get('fiscalyear'):
            if context.get('all_fiscalyear'):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
            else:
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = context['fiscalyear']
            if isinstance(context['fiscalyear'], (int, long)):
                fiscalyear_ids = [fiscalyear_ids]

        query_params['fiscalyear_ids'] = tuple(fiscalyear_ids) or (0,)
        state = context.get('state', False)
        where_move_state = ''
        where_move_lines_by_date = ''
        
        # By Rafiq
        where_move_lines_by_stream_line = ''
        stream_line_org = context.get('a1_id', False)

        if stream_line_org is not False and stream_line_org != '':
            if type(stream_line_org) is int:
                stream_line = stream_line_org
                query_params['stream_line'] = stream_line
                where_move_lines_by_stream_line = " AND " +obj+".a1_id = %(stream_line)s"
            else:
                stream_line = stream_line_org[0]
                query_params['stream_line'] = stream_line
                where_move_lines_by_stream_line = " AND " +obj+".a1_id = %(stream_line)s"           
#         where_move_lines_by_stream_line = ""
        
        if context.get('date_from') and context.get('date_to'):
            query_params['date_from'] = context['date_from']
            query_params['date_to'] = context['date_to']
            if initial_bal:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < %(date_from)s)"
            else:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= %(date_from)s AND date <= %(date_to)s)"

        if state:
            if state.lower() not in ['all']:
                query_params['state'] = state
                where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = %(state)s)"
        if context.get('period_from') and context.get('period_to') and not context.get('periods'):
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period, context['period_from'])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])
        if 'periods_special' in context:
            periods_special = ' AND special = %s ' % bool(context.get('periods_special'))
        else:
            periods_special = ''
        if context.get('periods'):
            query_params['period_ids'] = tuple(context['periods'])
            if initial_bal:
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date + where_move_lines_by_stream_line
                period_ids = fiscalperiod_obj.search(cr, uid, [('id', 'in', context['periods'])], order='date_start', limit=1)
                if period_ids and period_ids[0]:
                    first_period = fiscalperiod_obj.browse(cr, uid, period_ids[0], context=context)
                    query_params['date_start'] = first_period.date_start
                    query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s AND date_start <= %(date_start)s AND id NOT IN %(period_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date + where_move_lines_by_stream_line
            else:
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s AND id IN %(period_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date + where_move_lines_by_stream_line
        else:
            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date + where_move_lines_by_stream_line

        if initial_bal and not context.get('periods') and not where_move_lines_by_date:
            #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
            #so we have to invalidate this query
            raise osv.except_osv(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))

        if context.get('journal_ids'):
            query_params['journal_ids'] = tuple(context['journal_ids'])
            query += ' AND '+obj+'.journal_id IN %(journal_ids)s'

        if context.get('chart_account_id'):
            child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
            query_params['child_ids'] = tuple(child_ids)
            query += ' AND '+obj+'.account_id IN %(child_ids)s'

        query += company_clause
        return cr.mogrify(query, query_params)

 
