from odoo import models, fields, api, exceptions

class HrChecklistStatus(models.Model):
    _name = "hr.checklist.status"



    checklist_status_item_id = fields.Many2one('hr.exit.checklist.item', string='Name')
    checklist_type_id = fields.Many2one('hr.exit.checklist.type', string='Type')
    item_description = fields.Char(size=200, string='Description')
    receive_by = fields.Char(size=100, string='Received By')
    is_check = fields.Boolean(string='Checked')

    checklist_status_id = fields.Many2one('hr.emp.master.checklists', string="Checklist Status")
    status_line_ids = fields.One2many('hr.exit.configure.checklists.line', 'status_line_id')


