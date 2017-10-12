from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class CustomerCommissionConfigurationProduct(models.Model):
    _name="customer.commission.configuration.product"
    _order='id desc'

    old_value= fields.Float(string="Old Value", digits=(16,2), readonly = False)
    new_value= fields.Float(string="New Value", digits=(16,2), required=True)
    status = fields.Boolean(string='Status',default=True, required=True)

    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product", required=True,
                                 domain="([('sale_ok','=','True'),('type','=','consu')])")
    config_parent_id = fields.Many2one('customer.commission.configuration', ondelete='cascade')


    # show a warning when input data
    @api.onchange('new_value')
    def _onchange_new_value(self):
        if self.new_value > 100:
            raise UserError("[Error] 'New Value' must be between 0 to 100 !")

    #show a warning when click save burtton
    @api.constrains('new_value')
    def _check_value(self):
        if self.new_value > 100:
            raise Warning("[Error] 'New Value' must be between 0 to 100 !")

    # Show a msg for minus value
    @api.onchange('new_value', 'old_value')
    def _onchange_value(self):
        if self.new_value < 0 or self.old_value < 0:
            raise UserError('New value or Old value naver take negative value!')