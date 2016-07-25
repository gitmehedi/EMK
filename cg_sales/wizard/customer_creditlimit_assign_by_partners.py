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
from openerp.osv import fields, osv
from openerp.tools.translate import _

class creditlimit_partners(osv.osv_memory):

    _name ='creditlimit.partners'
    _description = 'Generate creditlimit for all selected partners'
    _columns = {
        'partner_ids': fields.many2many('res.partner', 'partner_limit_group_rel', 'limit_id', 'partner_id', 'Customers'),
    }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        partner_pool = self.pool.get('res.partner')
        limit_pool = self.pool.get('res.partner.limits')
        run_pool = self.pool.get('customer.creditlimit.assign')

        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['credit_limit'])
            print run_data
        limit_data = run_data.get('credit_limit', False)
        assign_id = run_data.get('id', False)
        assign_date =  time.strftime('%Y-%m-%d')        
        if not data['partner_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select customer(s) to generate limit(s)."))
        for partner in partner_pool.browse(cr, uid, data['partner_ids'], context=context):
            res = {
                'partner_id': partner.id,
                'assign_date': assign_date,
                'value': limit_data,
                'assign_id':assign_id,
                'state': 'draft',
            }
            
            limit_pool.create(cr, uid, res, context=context)
        
        return {'type': 'ir.actions.act_window_close'}

creditlimit_partners()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
