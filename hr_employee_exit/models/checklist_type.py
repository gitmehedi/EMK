from odoo import models, fields, api, exceptions,_
from psycopg2 import IntegrityError
from odoo.exceptions import UserError, ValidationError


class ChecklistType(models.Model):
    _name = 'hr.exit.checklist.type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    # Model Fields
    name = fields.Char(string='Name', size=100, required=True, help='Please enter name.')
    description = fields.Text(string='Description', size=500, help='Please enter description')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

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
                return super(ChecklistType, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    # _sql_constraints = [
    #     ('_check_name_uniq', 'unique(name)', "Checklist type name already exists!"),
    # ]
