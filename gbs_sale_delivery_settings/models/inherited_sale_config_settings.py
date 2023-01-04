from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    def _get_default_delivery_report_factory(self):
        return self.env.user.company_id.delivery_report_factory

    def _get_default_undelivered_report_factory(self):
        return self.env.user.company_id.undelivered_report_factory

    delivery_order_auto_generate = fields.Selection([
        (1, "Generate Delivery Order Automatically"),
        (0, 'Do Not Generate Delivery Order Automatically'),
    ], "Delivery Order Generating")

    delivery_report_factory = fields.Boolean(string="The Price Unit, Currency, Amount columns will not be showed on this report",
                                             default=lambda self: self._get_default_delivery_report_factory())
    undelivered_report_factory = fields.Boolean(string="The Price Unit, Currency, Amount columns will not be showed on this report",
                                                default=lambda self: self._get_default_undelivered_report_factory())
    sale_terms_condition = fields.Text(string="Sales/Invoice Terms and Conditions *")

    @api.multi
    def set_delivery_report_factory(self):
        if self.delivery_report_factory != self.company_id.delivery_report_factory:
            self.company_id.write({'delivery_report_factory': self.delivery_report_factory})

        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'delivery_report_factory', self.delivery_report_factory
        )

    @api.multi
    def set_undelivered_report_factory(self):
        if self.undelivered_report_factory != self.company_id.undelivered_report_factory:
            self.company_id.write({'undelivered_report_factory': self.undelivered_report_factory})

        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'undelivered_report_factory', self.undelivered_report_factory
        )

    @api.multi
    def set_sale_terms_condition(self):
        if self.sale_terms_condition != self.company_id.sale_terms_condition:
            self.company_id.write({'sale_terms_condition': self.sale_terms_condition})

        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'sale_terms_condition', self.sale_terms_condition
        )


class ResCompany(models.Model):
    _inherit = "res.company"

    delivery_report_factory = fields.Boolean(string="Delivery Report For Factory")
    undelivered_report_factory = fields.Boolean(string="Undelivered Report For Factory")
    sale_terms_condition = fields.Text(string="Sales/Invoice Terms and Conditions *")
