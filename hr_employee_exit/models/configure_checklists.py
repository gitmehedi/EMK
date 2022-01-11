from odoo import models, fields, api, exceptions,_
from psycopg2 import IntegrityError
from odoo.exceptions import UserError, ValidationError

class ConfigureChecklists(models.Model):
    _name='hr.exit.configure.checklists'
    _inherit = ['mail.thread','ir.needaction_mixin']

    
    #Model Fields
    name=fields.Char(string='Name', size=100, required=True, help='Please enter name.',track_visibility='onchange')
    notes=fields.Text(string='Notes', size=500, help='Please enter notes.',track_visibility='onchange')
    responsible_type = fields.Selection(selection=[('department', 'Department'), ('individual', 'Individual')],track_visibility='onchange')
    applicable_for = fields.Selection(selection=[('department', 'Department'), ('designation', 'Designation'), ('individual', 'Individual')],track_visibility='onchange')

    #Relational Fields
    applicable_department_id = fields.Many2one('hr.department', string='Applicable Department',track_visibility='onchange')
    applicable_empname_id = fields.Many2one('hr.employee', string='Applicable Employee',track_visibility='onchange')
    applicable_jobtitle_id = fields.Many2one('hr.job', string='Applicable Designation',track_visibility='onchange')
    responsible_userdepartment_id = fields.Many2one('hr.department', string='Responsible Department',track_visibility='onchange')
    responsible_username_id = fields.Many2one('hr.employee', string='Responsible User',track_visibility='onchange')
    checklists_ids = fields.One2many('hr.exit.configure.checklists.line','checklists_id')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )


    @api.onchange('responsible_type')
    def on_change_responsible_type(self):
        self.responsible_userdepartment_id=0
        self.responsible_username_id=0

    @api.onchange('applicable_for')
    def on_change_applicable_for(self):
        self.applicable_department_id=0
        self.applicable_empname_id=0
        self.applicable_jobtitle_id=0

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))
            try:
                return super(ConfigureChecklists, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


