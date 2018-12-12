from odoo import api, fields, models
from odoo.exceptions import UserError


class CustomerCommissionConfigurationProduct(models.Model):
    _name="customer.commission.configuration.product"
    _order='id desc'

    old_value= fields.Float(string="Old Value", compute='store_old_value',digits=(16,2), readonly = True, store=True)
    new_value= fields.Float(string="New Value", digits=(16,2), required=True)
    status = fields.Boolean(string='Status',default=True, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')


    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product", required=True,
                                 domain="([('sale_ok','=','True')])")
    config_parent_id = fields.Many2one('customer.commission.configuration', ondelete='cascade')

    @api.multi
    @api.onchange('product_id')
    def onchange_product(self):
        self.old_value = 0
        if self.product_id and self.config_parent_id.customer_id:
            commission = self.env['customer.commission'].search(
                [('product_id', '=', self.product_id.id), ('customer_id', '=', self.config_parent_id.customer_id.id),
                 ('status', '=', True)])

            if self.product_id.product_tmpl_id.commission_type == 'fixed':
                self.currency_id = self.env.user.company_id.currency_id.id
            else:
                self.currency_id = None

            if commission:
                for coms in commission:
                    self.old_value = coms.commission_rate
            else:
                self.old_value = 0

    @api.multi
    @api.depends('product_id')
    def store_old_value(self):
        for rec in self:
            if rec.product_id and rec.config_parent_id.customer_id:
                commission = self.env['customer.commission'].search(
                    [('product_id', '=', rec.product_id.id),
                    ('customer_id', '=', rec.config_parent_id.customer_id.id),
                    ('status', '=', True)])

                if commission:
                    for coms in commission:
                        rec.old_value = coms.commission_rate
                else:
                    rec.old_value = 0

    # show a warning when input data
    @api.multi
    @api.onchange('new_value')
    def _onchange_new_value(self):
        for coms in self:
            if coms.product_id.commission_type == 'percentage':
                if coms.new_value > 100:
                    raise UserError("[Error] 'New Value' must be between 0 to 100 !")

    #show a warning when click save burtton
    @api.multi
    @api.constrains('new_value')
    def _check_value(self):
        for coms in self:
            if coms.product_id.commission_type == 'percentage':
                if coms.new_value > 100:
                    raise Warning("[Error] 'New Value' must be between 0 to 100 !")

    # Show a msg for minus value
    @api.multi
    @api.onchange('new_value', 'old_value')
    def _onchange_value(self):
        for coms in self:
            if coms.new_value < 0 or self.old_value < 0:
                raise UserError('New value or Old value naver take negative value!')