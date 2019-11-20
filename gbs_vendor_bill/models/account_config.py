from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    head_branch_id = fields.Many2one('operating.unit', string='Head Branch')


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_head_branch_id(self):
        return self.env.user.company_id.head_branch_id

    head_branch_id = fields.Many2one('operating.unit', string='Head Branch',
                                     default=lambda self: self._get_default_head_branch_id())

    @api.multi
    def set_head_branch_id(self):
        if self.head_branch_id and self.head_branch_id != self.company_id.head_branch_id:
            self.company_id.write({'head_branch_id': self.head_branch_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'head_branch_id', self.head_branch_id.id)
