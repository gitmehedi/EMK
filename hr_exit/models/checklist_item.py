from openerp import models, fields, api, exceptions

class ChecklistItem(models.Model):
    _name='hr.exit.checklist.item'
    
    #Database fields
    checklist_type=fields.Many2one('hr.exit.checklist.type', ondelete='set null', string='Checklist Type', required=True, help='Please select checklist type.')
    name=fields.Char(string='Item Name', size=100, required=True, help='Please enter name.')
    keeper=fields.Many2one('hr.employee', ondelete='set null', string='Item Keeper', required=True, help='Please enter item keeper name.')
    description=fields.Text(string='Description', size=500, help='Please enter description.')
    is_active=fields.Boolean(string='Active', default=True)