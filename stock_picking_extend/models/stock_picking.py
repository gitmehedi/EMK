# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"

    @api.model
    def _get_default_picking_type(self):
        if self.env.context.get('default_transfer_type') == 'receive':
            picking_type_objs = self.env['stock.picking.type'].search(
                    [('operating_unit_id', '=', self.env.user.default_operating_unit_id.id),
                     ('code', '=', 'incoming')])
            return picking_type_objs[0].id

    transfer_type = fields.Selection([
        ('receive', 'Receive'),('loan', 'Loan')])
    receive_type = fields.Selection([
        ('loan', 'Loan'),
        ('other', 'Other')],
        readonly=True,states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True,default = _get_default_picking_type,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    doc_count = fields.Integer(compute='_compute_attached_docs', string="Number of documents attached")

    challan_bill_no = fields.Char(
        string='Challan Bill No',
        readonly=True,
        states={'draft': [('readonly', False)],'assigned':[('readonly', False)]})

    @api.constrains('challan_bill_no')
    def _check_unique_constraint(self):
        if self.partner_id and self.challan_bill_no:
            filters = [['challan_bill_no', '=ilike', self.challan_bill_no], ['partner_id', '=', self.partner_id.id]]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('[Unique Error] Challan Bill must be unique for %s !') % self.partner_id.name)

    @api.one
    def _compute_attached_docs(self):
        attachment = self.env['ir.attachment']
        if self.origin:
            origin_picking_objs = self.search(['|', ('name', '=', self.origin),('origin', '=', self.origin)])
            res = self.ids + origin_picking_objs.ids
        else:
            res = self.ids
        list_res =list(set(res))
        self.doc_count = len(attachment.search([('res_model', '=', 'stock.picking'), ('res_id', '=', list_res)]))

        # for id in set(res):
        #     picking_attachments = attachment.search([('res_model', '=', 'stock.picking'), ('res_id', '=', id)])
        #     self.doc_count = len([v.id for v in picking_attachments])

    @api.multi
    def attachment_tree_view(self):
        if self.origin:
            origin_picking_objs = self.search(['|',('name', '=', self.origin),('origin', '=', self.origin)])
            res = self.ids + origin_picking_objs.ids
        else:
            res = self.ids
        domain = [('res_model', '=', 'stock.picking'),('res_id', 'in', res)]
        res_id = self.ids and self.ids[0] or False
        return {
            'name': 'Attachments',
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    show_on_dashboard = fields.Boolean(string='Show Picking Type on dashboard', help="Whether this Picking Type should be displayed on the dashboard or not", default=True)


# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     @api.model
#     def create(self, vals):
#         if not vals['price_unit']:
#             product = self.env['product.product'].browse(vals['product_id'])
#             vals['price_unit'] = product.standard_price
#         res = super(StockMove, self).create(vals)
#         return res