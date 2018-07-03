from odoo import models, fields, api, exceptions

class ChecklistItem(models.Model):
    _name='hr.exit.checklist.item'

    # Model Fields
    name=fields.Char(string='Item Name', size=100, required=True, help='Please enter name.')
    description=fields.Text(string='Description', size=500, help='Please enter description.')
    is_active=fields.Boolean(string='Active', default=True)

    # Relational Fields
    checklist_type=fields.Many2one('hr.exit.checklist.type', ondelete='set null',
                                   string='Checklist Type',domain=[('is_active','=',True)],
                                   required=True, help='Please select checklist type.')
    checklist_status_item_ids = fields.One2many('hr.checklist.status','checklist_status_item_id', string='Checklist Status')

    checklist_item_id = fields.Many2one('hr.exit.configure.checklists.line')



