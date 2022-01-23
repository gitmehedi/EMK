from odoo import models, fields, api, exceptions,_
from psycopg2 import IntegrityError
from odoo.exceptions import UserError, ValidationError

class ChecklistItem(models.Model):
    _name='hr.exit.checklist.item'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    # Model Fields
    name = fields.Char(string='Item Name', size=100, required=True, help='Please enter name.',track_visibility='onchange')
    description = fields.Text(string='Description', size=500, help='Please enter description.',track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    # Relational Fields
    checklist_type = fields.Many2one('hr.exit.checklist.type', ondelete='set null',
                                   string='Checklist Type',domain=[('state','=','approve')],track_visibility='onchange',
                                   required=True, help='Please select checklist type.')
    #checklist_status_item_ids = fields.One2many('hr.checklist.status','checklist_status_item_id', string='Checklist Status')

    checklist_item_id = fields.Many2one('hr.exit.configure.checklists.line')

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
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
                return super(ChecklistItem, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    # _sql_constraints = [
    #     ('_check_name_uniq', 'unique(name)', "Checklist item name already exists!"),
    # ]



