from odoo import api, fields, models,_
from openerp.exceptions import UserError, ValidationError


class CustomerCommissionConfigurationCustomer(models.Model):
    _name = "customer.commission.configuration.customer"
    _order = 'id desc'

    old_value = fields.Float(string="Old Value", compute='store_old_value', digits=(16, 2), readonly = False,store=True)
    new_value = fields.Float(string="New Value",required=True)
    status = fields.Boolean(string='Status', default=True, required=True)

    """ Relational Fields """
    customer_id = fields.Many2one('res.partner', string="Customer", required=True, domain="([('customer','=','True')])")
    config_parent_id = fields.Many2one('customer.commission.configuration', ondelete='cascade')

    @api.onchange('customer_id')
    def onchange_customer(self):
        self.old_value = 0
        if self.customer_id and self.config_parent_id.product_id:
            commission = self.env['customer.commission'].search(
                [('customer_id', '=', self.customer_id.id), ('product_id', '=', self.config_parent_id.product_id.id),
                 ('status', '=', True)])

            self.old_value = commission.commission_rate if commission else 0

    @api.depends('customer_id')
    def store_old_value(self):
        for rec in self:
            if rec.customer_id and rec.config_parent_id.product_id:
                commission = self.env['customer.commission'].search(
                    [('customer_id', '=', rec.customer_id.id), ('product_id', '=', rec.config_parent_id.product_id.id),
                     ('status', '=', True)])

                rec.old_value = commission.commission_rate if commission else 0

    """All function which process data and operation"""

    @api.constrains('new_value')
    def _check_unique_constraint(self):
            if self.new_value > 100:
                raise Warning("[Error]'New Value' must be between 0 to 100 !")