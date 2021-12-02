from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    batch_date = fields.Date(string='Application Date', default=fields.Date.today, required=True)

    @api.multi
    def set_batch_date(self):
        if self.batch_date:
            self.company_id.write({'batch_date': self.batch_date})
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'batch_date', self.batch_date)


class ResCompany(models.Model):
    _inherit = "res.company"

    batch_date = fields.Date(string='Application Date', default=fields.Date.today)
