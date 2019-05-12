from odoo import api, fields, models, _
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class Branch(models.Model):
    _name = 'operating.unit'
    _order = 'name desc'
    _inherit = ['operating.unit', 'mail.thread']

    code = fields.Char('Code', required=True, size=3, track_visibility='onchange')
    name = fields.Char('Name', required=True, size=50, track_visibility='onchange')
    active = fields.Boolean('Active', default=True, track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, track_visibility='onchange', default=lambda self:
        self.env['res.company']._company_default_get('account.account'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, default=lambda self:
    self.env['res.company']._company_default_get('account.account'))
    branch_type = fields.Selection([('metro', 'Metro'), ('urban', 'Urban'), ('rural', 'Rural')],
                                   string='Location of Branch', track_visibility='onchange', required=True)

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.multi
    def unlink(self):
        try:
            return super(Branch, self).unlink()
        except IntegrityError:
            raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                    "- deletion: you may be trying to delete a record while other records still reference it"))

