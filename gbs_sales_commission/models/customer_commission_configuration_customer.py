from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CustomerCommissionConfigurationCustomer(models.Model):
    _name = "customer.commission.configuration.customer"
    _order = 'id desc'

    old_value = fields.Float(string="Old Value", compute='store_old_value', readonly=True, store=True)
    new_value = fields.Float(string="New Value", required=True)
    status = fields.Boolean(string='Status', default=True, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')

    """ Relational Fields """
    customer_id = fields.Many2one('res.partner', string="Customer", required=True, domain="[('customer', '=', True),('parent_id', '=', False)]")
    config_parent_id = fields.Many2one('customer.commission.configuration', ondelete='cascade')

    @api.onchange('customer_id')
    def onchange_customer(self):
        self.old_value = 0
        if self.customer_id and self.config_parent_id.product_id:
            commission = self.env['customer.commission'].search(
                [('customer_id', '=', self.customer_id.id), ('product_id', '=', self.config_parent_id.product_id.id),
                 ('status', '=', True)])

            if self.config_parent_id.product_id.product_tmpl_id.commission_type == 'fixed':
                self.currency_id = self.env.user.company_id.currency_id.id
            else:
                self.currency_id = None

            if commission:
                for coms in commission:
                    self.old_value = coms.commission_rate
            else:
                self.old_value = 0

    @api.depends('customer_id')
    def store_old_value(self):
        for rec in self:
            if rec.customer_id and rec.config_parent_id.product_id:
                commission = self.env['customer.commission'].search(
                    [('customer_id', '=', rec.customer_id.id), ('product_id', '=', rec.config_parent_id.product_id.id),
                     ('status', '=', True)])

                if commission:
                    for coms in commission:
                        rec.old_value = coms.commission_rate
                else:
                    rec.old_value = 0

    # show a warning when input data
    @api.onchange('new_value')
    def _onchange_new_value(self):
        if self.config_parent_id.product_id.commission_type == 'percentage':
            if self.new_value > 100:
                raise UserError(_("[Error] 'New Value' must be between 0 to 100 !"))

    # show a warning when click save burtton
    @api.constrains('new_value')
    def _check_value(self):
        if self.config_parent_id.product_id.commission_type == 'percentage':
            if self.new_value > 100:
                raise Warning("[Error] 'New Value' must be between 0 to 100 !")

    # Show a msg for minus value
    @api.onchange('new_value', 'old_value')
    def _onchange_value(self):
        if self.new_value < 0 or self.old_value < 0:
            raise UserError(_('New value or Old value naver take negative value!'))
