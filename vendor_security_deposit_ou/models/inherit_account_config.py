from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    security_deposit_operating_unit_id = fields.Many2one('operating.unit', string='Security Deposit Branch',
                                                         help="Branch for Security Deposit")


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_security_deposit_operating_unit_id(self):
        return self.env.user.company_id.security_deposit_operating_unit_id

    security_deposit_operating_unit_id = fields.Many2one('operating.unit', string='Security Deposit Branch',
                                                         default=lambda self: self._get_default_security_deposit_operating_unit_id(),
                                                         help="Branch for Security Deposit")

    @api.multi
    def set_security_deposit_operating_unit_id(self):
        if self.security_deposit_operating_unit_id and \
                        self.security_deposit_operating_unit_id != self.company_id.security_deposit_operating_unit_id:
            self.company_id.write({'security_deposit_operating_unit_id': self.security_deposit_operating_unit_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'security_deposit_operating_unit_id', self.security_deposit_operating_unit_id.id)
