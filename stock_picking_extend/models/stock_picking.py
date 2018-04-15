# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_default_picking_type(self):
        if self.env.context.get('default_transfer_type') == 'receive':
            picking_type_objs = self.env['stock.picking.type'].search(
                    [('warehouse_id.operating_unit_id', '=', self.env.user.default_operating_unit_id.id),
                     ('code', '=', 'incoming')])
            return picking_type_objs[0].id

    transfer_type = fields.Selection([
        ('loan', 'Loan'),
        ('receive', 'Receive'),
        ('delivery', 'Delivery'),
        ('transfer', 'Transfer')])
    receive_type = fields.Selection([
        ('loan', 'Loan'),
        ('other', 'Other')],
        readonly=True,states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True,default = _get_default_picking_type,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.one
    def _get_attached_docs(self):
        attachment = self.env['ir.attachment']
        origin_picking_objs = self.search([('name', '=', self.origin)])
        res = self.ids + origin_picking_objs.ids
        for id in res:
            employee_attachments = attachment.search([('res_model', '=', 'stock.picking'), ('res_id', '=', id)])
            self.doc_count = len([v.id for v in employee_attachments])

    doc_count = fields.Integer(compute=_get_attached_docs, string="Number of documents attached")

    @api.multi
    def attachment_tree_view(self):
        origin_picking_objs = self.search([('name', '=', self.origin)])
        res = self.ids + origin_picking_objs.ids
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
