from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError
from odoo.addons.opa_utility.helper.utility import Utility


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'mail.thread', 'ir.needaction_mixin']

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')

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

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise ValidationError(_(Utility.UNIQUE_WARNING))

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Utility.UNLINK_WARNING))
            try:
                return super(ProductProduct, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Utility.UNLINK_INT_WARNING))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'mail.thread', 'ir.needaction_mixin']

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise ValidationError(_(Utility.UNIQUE_WARNING))

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

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
                raise ValidationError(_(Utility.UNLINK_WARNING))
            try:
                return super(ProductTemplate, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Utility.UNLINK_INT_WARNING))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]
