# -*- coding: utf-8 -*-

from odoo import fields, models, api


class hr_employee(models.Model):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"
    
    
    @api.multi
    def attachment_tree_view(self, context):
        domain = ['&', ('res_model', '=', 'hr.employee'), ('res_id', 'in', self.ids)]
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
    
    @api.one
    def _get_attached_docs(self):
        attachment = self.env['ir.attachment']
        for id in self.ids:
            employee_attachments = attachment.search([('res_model', '=', 'hr.employee'), ('res_id', '=', id)])
            self.doc_count = len([v.id for v in employee_attachments])

    doc_count = fields.Integer(compute=_get_attached_docs, string="Number of documents attached")
