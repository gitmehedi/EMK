from openerp import models, fields, api, exceptions

class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"
    
    check_list_type_id = fields.Many2one('hr.exit.checklist.type', string="Checklist Types")
    check_list_item_id = fields.Many2one('hr.exit.checklist.item', string="Employee Checklist")

    # Relational fields
    check_list_line_id = fields.Many2one('hr.exit.configure.emp.checklists')
    checklists_id = fields.Many2one('hr.exit.configure.checklists')
    
