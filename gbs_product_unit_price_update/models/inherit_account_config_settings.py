from odoo import fields, models, api


class InheritedAccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_include_product_purchase_cost(self):
        return self.env.user.company_id.include_product_purchase_cost

    include_product_purchase_cost = fields.Boolean(string='Include Product Cost',default=lambda self: self._get_default_include_product_purchase_cost())


    @api.multi
    def set_include_product_purchase_cost(self):
        if self.include_product_purchase_cost != self.company_id.include_product_purchase_cost:
            self.company_id.write({'include_product_purchase_cost': self.include_product_purchase_cost})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'include_product_purchase_cost', self.include_product_purchase_cost)


class ResCompany(models.Model):
    _inherit = "res.company"

    include_product_purchase_cost = fields.Boolean(string='Include Product Purchase Cost')
