from odoo import api, fields, models, _

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_sundry_account_id(self):
        return self.env.user.company_id.sundry_account_id

    sundry_account_id = fields.Many2one('account.account',string='Sundry Account',required=True,
                                                  default=lambda self: self._get_default_sundry_account_id(),
                                                  help="Sundry account used for Vendor bill payments")
    @api.multi
    def set_default_sundry_account_id(self):
        if self.sundry_account_id and self.sundry_account_id != self.company_id.sundry_account_id:
            self.company_id.write({'sundry_account_id': self.sundry_account_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'sundry_account_id', self.sundry_account_id.id)


    # @api.model
    # def create(self, vals):
    #     if 'sundry_account_id' in vals:
    #         company = self.env['res.company'].browse(vals.get('company_id'))
    #         company.write({
    #             'sundry_account_id': vals.get('sundry_account_id'),
    #         })
    #     res = super(AccountConfigSettings, self).create(vals)
    #     return res