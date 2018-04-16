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
        ('receive', 'Receive')])
    receive_type = fields.Selection([
        ('loan', 'Loan'),
        ('other', 'Other')],
        readonly=True,states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True,default = _get_default_picking_type,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False, states={'done': [('readonly', True)]},
                                help="Completion Date of Transfer",default=fields.Datetime.now())


    doc_count = fields.Integer(compute='_compute_attached_docs', string="Number of documents attached")

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
