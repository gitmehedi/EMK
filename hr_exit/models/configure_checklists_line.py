from openerp import models, fields, api, exceptions

class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"
    
    check_list_type_id = fields.Many2one('hr.exit.checklist.type', string="Checklist Types")
    
    # Relational fields
    checklists_id = fields.Many2one('hr.exit.configure.checklists',)
    
