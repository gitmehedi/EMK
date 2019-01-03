from odoo import api,fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockIndentConfigSettings(models.Model):
    _name = 'stock.indent.config.settings'
    _inherit = 'res.config.settings'

    @api.multi
    def _get_default(self):
        query = """select days_of_backdating_indent from stock_indent_config_settings order by id desc limit 1"""
        self.env.cr.execute(query)
        days_value = self.env.cr.fetchone()
        if days_value:
            return days_value[0]

    days_of_backdating_indent = fields.Integer(size=4, default=_get_default)

    @api.multi
    @api.constrains('days_of_backdating_indent')
    def _check_days_of_backdating_indent(self):
        for rec in self:
            if rec.days_of_backdating_indent<0:
                raise ValidationError(_("You can't set negative value."))

    #
    # @api.model
    # def create(self, vals):
    #     config_id = super(StockIndentConfigSettings, self).create(vals)
    #     return config_id