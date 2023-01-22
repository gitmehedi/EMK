from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    security_deposit_sequence_id = fields.Many2one('sub.operating.unit', string='Security Deposit Sequence',
                                                   help="Sequence for Security Deposit")


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_sequence_id(self):
        return self.env.user.company_id.security_deposit_sequence_id

    security_deposit_sequence_id = fields.Many2one('sub.operating.unit', string='Security Deposit Sequence',
                                                   help="Sequence for Security Deposit", required=True,
                                                   default=lambda self: self._get_default_sequence_id())

    @api.multi
    def set_security_deposit_sequence_id(self):
        if self.security_deposit_sequence_id and \
                        self.security_deposit_sequence_id != self.company_id.security_deposit_sequence_id:
            self.company_id.write({'security_deposit_sequence_id': self.security_deposit_sequence_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'security_deposit_sequence_id', self.security_deposit_sequence_id.id)