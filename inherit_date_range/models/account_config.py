from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = "res.company"

    retain_earning_id = fields.Many2one('account.account', string='Retain Earnings', required=True)
    general_account_id = fields.Many2one('account.account', string='General Account', required=True)
    eoy_type = fields.Selection([('general', 'General'), ('banking', 'Banking')], string='EOY Type', required=True)

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_retain_earning_id(self):
        return self.env.user.company_id.retain_earning_id

    def _get_default_general_account_id(self):
        return self.env.user.company_id.general_account_id


    retain_earning_id = fields.Many2one('account.account', string='Retain Earnings', required=True,
                                        default=lambda self: self._get_default_retain_earning_id())
    general_account_id = fields.Many2one('account.account', string='General Account', required=True,
                                         default=lambda self: self._get_default_general_account_id())
    eoy_type = fields.Selection([('general', 'General'), ('banking', 'Banking')], string='EOY Type', required=True)

    @api.multi
    def set_retain_earning_id(self):
        if self.retain_earning_id:
            self.company_id.write({'retain_earning_id': self.retain_earning_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'retain_earning_id',self.retain_earning_id.id )

    @api.multi
    def set_general_account_id(self):
        if self.general_account_id:
            self.company_id.write({'general_account_id': self.general_account_id.id})
        return self.env['ir.values'].sudo().set_default('account.config.settings','general_account_id', self.general_account_id.id)

    @api.multi
    def set_eoy_type(self):
        if self.eoy_type:
            self.company_id.write({'eoy_type': self.eoy_type})
        return self.env['ir.values'].sudo().set_default('account.config.settings','eoy_type', self.eoy_type)


