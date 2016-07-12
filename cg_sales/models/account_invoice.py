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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    
    _inherit = "account.invoice"
    
    @api.multi
    def invoice_validate(self):
        #print "----------30---------------", self.partner_id.total_outstanding
        res = super(account_invoice, self).invoice_validate()
        self.write({'outstanding': self.partner_id.total_outstanding})
        return res
    
    def _check_credit_limit(self, cr, uid, invoice, context=None):
        #print "_check_credit_limit"
        if invoice:
            soobj = self.pool.get('sale.order')
            so_ids = soobj.search(cr, uid, [('name','=',invoice.origin)])
            if so_ids:
                so = soobj.browse(cr, uid, so_ids[0], context)
                if so and so.so_type == 'invf':                
                    if ((invoice.amount_total + so.partner_id.credit)<so.partner_id.credit_limit):
                        return True
                    else:
                        user = self.pool.get('res.users').browse(cr, uid, uid, context)
                        grpobj = self.pool.get('res.groups')
                        grp_ids = grpobj.search(cr, uid, [('name','=','Invoice Validation (Customer Credit Limit)')])
                        grp = grpobj.browse(cr, uid, grp_ids[0])
                                        
                        if grp in user.groups_id:
                            return True
                    
                    raise osv.except_osv('Warning!',('To proceed please check the customer credit limit.'))
                    return False
                else:
                    return True
            
        return True
    
    def action_date_assign(self, cr, uid, ids, *args):
        print "action_date_assign"
        for invoice in self.browse(cr, uid, ids):
            if not self._check_credit_limit(cr, uid, invoice, context=None):
                return False
            
        res = super(account_invoice, self).action_date_assign(cr, uid, ids, *args)
        return res
    
    def _get_area(self, cr, uid, ids, name, arg, context=None):
        res = {}
        so_pool = self.pool.get('sale.order')
        for invoice in self.browse(cr, uid, ids, context=context):
            so_ids = so_pool.search(cr, uid, [('name','=',invoice.origin)])
            if so_ids:
                order = so_pool.browse(cr, uid, so_ids[0], context=context)
                res[invoice.id] = order.area_id.id or False
            
        return res
    
    @api.multi
    def _get_so(self):
        so_obj = self.env['sale.order']
        for invoice in self:
            invoice.so_id = False
            if invoice.origin:
                so =  self.env['sale.order'].search([['name', '=', invoice.origin]])
                if so:
                    invoice.so_id = so.id
    

                    
    
    so_id = fields.Many2one('sale.order', string='Sale Order Ref', compute='_get_so', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", related='so_id.warehouse_id')
    area_id = fields.Many2one('sale.area', string='Sales Area', compute='_get_area', store=True,)
    outstanding = fields.Float(string='Outstanding', digits=dp.get_precision('Account'), readonly=True)
      

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
