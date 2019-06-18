from odoo import api, fields, models, _

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_sundry_account_id(self):
        return self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)], limit=1)

    sundry_account_id = fields.Many2one('account.account',string='Sundry account',required=True,
                                                  default=lambda self: self._get_default_sundry_account_id(),
                                                  help="Sundry account used for Vendor bill payments")
    @api.multi
    def set_default_sundry_account_id(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'sundry_account_id', self.sundry_account_id.id)

    @api.model
    def create(self, vals):
        if 'sundry_account_id' in vals:
            company = self.env['res.company'].browse(vals.get('company_id'))
            company.write({
                'sundry_account_id': vals.get('sundry_account_id'),
            })
        res = super(AccountConfigSettings, self).create(vals)
        return res