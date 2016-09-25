from openerp import models, fields, api, exceptions

class ConfigureChecklists(models.Model):
    _name='hr.exit.configure.checklists'
    
    #Model Fields
    code=fields.Char(string='Code', size=50, help='Please enter code.')
    name=fields.Char(string='Name', size=100, required=True, help='Please enter name.')
    responsible_type=fields.Selection(selection=[('department', 'Department'),('individual','Individual')])
    responsible_userdepartment=fields.Many2one('hr.department', ondelete='set null', string='Responsible Department', help='Please enter responsible department name.')
    responsible_username=fields.Many2one('hr.employee',string='Responsible User', help='Please enter responsible user name.')
    notes=fields.Text(string='Notes', size=500, help='Please enter notes.')
    is_active=fields.Boolean(string='Active', default=True)
    
    #Relational Fields
    checklists_line_ids = fields.One2many('hr.exit.configure.checklists.line','checklists_line_id')
    #checklists_ids = fields.One2many('hr.exit.configure.checklists.line','checklists_id')
    
    @api.onchange('responsible_type')
    def on_change_responsible_type(self):
        self.responsible_userdepartment=0
        self.responsible_username=''