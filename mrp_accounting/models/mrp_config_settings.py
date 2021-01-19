from odoo import fields, models, api, _


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    stock_valuation_accounting = fields.Boolean(string='Stock Valuation')
    cogs_accounting = fields.Boolean(string='COGS Entry')

    @api.multi
    def set_stock_valuation_accounting(self):
        if self.stock_valuation_accounting != self.company_id.stock_valuation_accounting:
            self.company_id.write({'stock_valuation_accounting': self.stock_valuation_accounting})
        return self.env['ir.values'].sudo().set_default(
            'mrp.config.settings', 'stock_valuation_accounting', self.stock_valuation_accounting)

    @api.multi
    def set_cogs_accounting(self):
        if self.cogs_accounting != self.company_id.cogs_accounting:
            self.company_id.write({'cogs_accounting': self.cogs_accounting})
        return self.env['ir.values'].sudo().set_default(
            'mrp.config.settings', 'cogs_accounting', self.cogs_accounting)


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_valuation_accounting = fields.Boolean(string='Stock Valuation')
    cogs_accounting = fields.Boolean(string='COGS Entry')
