# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class WorkOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Contains production terms named CM, FOB'
    _order = 'id desc'

    wcode = fields.Char(string="Code")

    purchase_type = fields.Selection([('purchaseorder', 'Purchase'), ('workorder', 'Work Order')],
                                     default='purchaseorder')
    payment_terms = fields.Text(string='Payment Terms')

    def create(self, cr, uid, vals, context=None):
        if 'purchase_type' in vals:
            if vals.get('name', '/') == '/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'wcode', context=context) or '/'


            context = dict(context or {}, mail_create_nolog=True)
        return super(WorkOrder, self).create(cr, uid, vals, context=context)


class WorkOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    production_term_id = fields.Many2one('purchase.production.terms', string="Production Term")
    remarks = fields.Text(string='Remarks')
