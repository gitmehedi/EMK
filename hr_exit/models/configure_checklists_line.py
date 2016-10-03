from openerp import models, fields, api, exceptions

class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"

    check_list_type_id = fields.Many2one('hr.exit.checklist.type', string="Checklist Types")
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', string='Checklist Item', required=True)

    # Relational fields
   # checklists_id = fields.Many2one('hr.exit.configure.checklists',)
    checklists_line_id = fields.Many2one('hr.exit.configure.checklists')

