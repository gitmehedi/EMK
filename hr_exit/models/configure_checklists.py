from odoo import models, fields, api, exceptions

class ConfigureChecklists(models.Model):
    _name='hr.exit.configure.checklists'
    
    #Model Fields
    name=fields.Char(string='Name', size=100, required=True, help='Please enter name.')
    responsible_type=fields.Selection(selection=[('department', 'Department'),('individual','Individual')])
    applicable_for=fields.Selection(selection=[('department', 'Department'),('designation','Designation'),('individual','Individual')])
    applicable_department_id=fields.Many2one('hr.department', string='Applicable Department')
    applicable_empname_id=fields.Many2one('hr.employee',string='Applicable Employee')
    applicable_jobtitle_id=fields.Many2one('hr.job',string='Applicable Designation')
    responsible_userdepartment_id=fields.Many2one('hr.department', string='Responsible Department')
    responsible_username_id=fields.Many2one('hr.employee',string='Responsible User')
    notes=fields.Text(string='Notes', size=500, help='Please enter notes.')
    is_active=fields.Boolean(string='Active', default=True)
    
    #Relational Fields   
    checklists_ids = fields.One2many('hr.exit.configure.checklists.line','checklists_id')


    @api.onchange('responsible_type')
    def on_change_responsible_type(self):
        self.responsible_userdepartment_id=0
        self.responsible_username_id=0

    @api.onchange('applicable_for')
    def on_change_applicable_for(self):
        self.applicable_department_id=0
        self.applicable_empname_id=0
        self.applicable_jobtitle_id=0