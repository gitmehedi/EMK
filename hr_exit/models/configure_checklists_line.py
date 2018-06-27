from odoo import models, fields, api, exceptions

class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"

    check_list_type_id = fields.Many2one('hr.exit.checklist.type', string="Checklist Types")
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', string='Checklist Item', required=True)
    remarks = fields.Text(string='Remarks')
    status = fields.Selection([('received','Received'),('not_received','Not Received')],'Status',default='received')

    # Relational fields
    checklists_id = fields.Many2one('hr.emp.exit.req',)
    checklists_line_id = fields.Many2one('hr.exit.configure.checklists')
    responsible_department = fields.Many2one('hr.department', ondelete='set null', string='Responsible Department')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User')

