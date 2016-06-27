from openerp import models, fields, api, exceptions

class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"

    # for employee checklist
    receive_by = fields.Char(string='Receive By')
    is_check = fields.Boolean(string='Checked')
    checklist_item_ids = fields.One2many('hr.exit.checklist.item','checklist_item_id')
    checklist_line_id = fields.Many2one('hr.configure.emp.checklists')

    #for item type
    check_list_type_id = fields.Many2one('hr.exit.checklist.type', string="Checklist Types")

    # Relational fields
    checklists_id = fields.Many2one('hr.exit.configure.checklists',)

