# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class InheritedPurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'ir.needaction_mixin']
    _description = 'Inherited Purchase Order'

    is_service_order = fields.Boolean(string='Service Order',
                                      default=lambda self: self.env.context.get('is_service_order') or False)

    service_order_creator = fields.Many2one('res.users', 'Creator', default=lambda self: self.env.user, track_visibility='onchange')

    purchase_from = fields.Selection([('own', 'Own'), ('ho', 'HO')],
                                     string="Purchase From")


    @api.model
    def create(self, vals):
        operating_unit_id = self.env['operating.unit'].browse(vals['operating_unit_id'])
        if vals.get('is_service_order'):
            vals['name'] = self.env['ir.sequence'].next_by_code_new('service.order', datetime.today(),
                                                                    operating_unit_id) or '/'

        return super(InheritedPurchaseOrder, self).create(vals)



    @api.multi
    def button_confirm(self):
        if self.is_service_order:
            self.write({'region_type':'local','purchase_by': 'credit','operating_unit_id': self.operating_unit_id.id,'state':'done'})
        else:
            res_wizard_view = self.env.ref('gbs_purchase_order.purchase_order_type_wizard')
            res = {
                'name': _('Please Select LC Region Type and Purchase By before approve'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': res_wizard_view and res_wizard_view.id or False,
                'res_model': 'purchase.order.type.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'context': {'region_type': self.region_type or False,
                            'purchase_by': self.purchase_by or False,
                            'operating_unit_id': self.operating_unit_id.id},
                'target': 'new',
            }

            # res['return_original_method'] = super(PurchaseOrder, self).button_confirm()
            return res

    @api.model
    def _needaction_domain_get(self):
        domain = [
            ('state', 'in', ['draft'])]
        if len(domain) == 0:
            return False
        return domain


    @api.multi
    def print_service_order(self):
        data = {}
        data['active_id'] = self.id
        return self.env['report'].get_action(self, 'gbs_samuda_service_order.report_service_order', data)

    @api.multi
    @api.constrains('order_line')
    def _check_exist_product_in_line(self):
        for purchase in self:
            exist_product_list = []
            for line in purchase.order_line:
                if line.product_id.id in exist_product_list:
                    raise ValidationError(_('Product should be one per line.'))
                exist_product_list.append(line.product_id.id)


