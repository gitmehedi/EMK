from odoo import models, fields, api, exceptions

class ChecklistType(models.Model):
    _name = 'hr.exit.checklist.type'

    # Model Fields
    name = fields.Char(string='Name', size=100, required=True, help='Please enter name.')
    description = fields.Text(string='Description', size=500, help='Please enter description')
    is_active = fields.Boolean(string='Active', default=True)


    _sql_constraints = [
        ('_check_name_uniq', 'unique(name)', "Checklist type name already exists!"),
    ]
