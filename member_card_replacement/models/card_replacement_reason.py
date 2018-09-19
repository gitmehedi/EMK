from odoo import models, fields, api, _


class MemberCardReplacement(models.Model):
    _name = 'member.card.replacement.reason'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, track_visibility="onchange")
    status = fields.Boolean(default=True, string="Status", track_visibility="onchange")

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
