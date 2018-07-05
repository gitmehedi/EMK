from odoo import models, fields, api, exceptions

class ChecklistItem(models.Model):
    _name='hr.exit.checklist.item'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    # Model Fields
    name=fields.Char(string='Item Name', size=100, required=True, help='Please enter name.',track_visibility='onchange')
    description=fields.Text(string='Description', size=500, help='Please enter description.',track_visibility='onchange')
    is_active=fields.Boolean(string='Active', default=True,track_visibility='onchange')

    # Relational Fields
    checklist_type=fields.Many2one('hr.exit.checklist.type', ondelete='set null',
                                   string='Checklist Type',domain=[('is_active','=',True)],track_visibility='onchange',
                                   required=True, help='Please select checklist type.')
    #checklist_status_item_ids = fields.One2many('hr.checklist.status','checklist_status_item_id', string='Checklist Status')

    checklist_item_id = fields.Many2one('hr.exit.configure.checklists.line')

    _sql_constraints = [
        ('_check_name_uniq', 'unique(name)', "Checklist item name already exists!"),
    ]



