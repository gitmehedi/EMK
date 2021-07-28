# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class project_task(models.Model):
    _inherit = 'project.task'

    @api.multi
    def tasks_issue_count(self):
        ir_model_data = self.env['ir.model.data']
        search_view_id = ir_model_data.get_object_reference('project_issue', 'view_project_issue_filter')[1]
        if self and search_view_id:
            self[0].task_issue_count = self[0].env['project.issue'].search_count([('task_id','=',self[0].id)])
        return{
            'name':'Issues',
            'res_model':'project.issue',
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'list,kanban,form,calendar,pivot,graph',
            'domain': [('task_id', '=',self[0].id )],
            'search_view_id':search_view_id,
         }

    task_issue_count = fields.Integer(compute=tasks_issue_count,string="Task Count")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: