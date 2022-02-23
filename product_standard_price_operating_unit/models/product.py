# import of odoo
import logging
import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_standard_price_ids = fields.One2many('product.standard.price', 'product_id', 'Product Cost Price')
    product_standard_price_history_ids = fields.One2many('product.price.history', 'product_id', 'Product Cost Price History')

    @api.multi
    def _set_standard_price(self, value):
        pass

    @api.multi
    def _set_product_standard_price(self, value):
        operating_unit_id = self.env.context.get('operating_unit_id')
        if operating_unit_id:
            PriceHistory = self.env['product.price.history']
            for product in self:
                PriceHistory.create({
                    'product_id': product.id,
                    'cost': value,
                    'company_id': self._context.get('force_company', self.env.user.company_id.id),
                    'operating_unit_id': operating_unit_id,
                    'datetime': self.env.context.get('datetime_of_price_history') or fields.Datetime.now()
                })
        else:
            _logger.info("SAMUDA-CUSTOM-ERROR: [VALIDATION] operating unit not found in the context")
            # for testing purpose
            # raise ValidationError(_('Operating Unit Not Found in the context.'))

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        for line in product.product_standard_price_ids:
            product.with_context(operating_unit_id=line.operating_unit_id.id)._set_product_standard_price(line.cost)

        return product

    @api.multi
    def write(self, values):
        res = super(ProductProduct, self).write(values)
        if 'product_standard_price_ids' in values:
            for val in values['product_standard_price_ids']:
                if val[0] == 0:
                    # create
                    operating_unit_id = val[2]['operating_unit_id']
                    self.with_context(operating_unit_id=operating_unit_id)._set_product_standard_price(val[2]['cost'])
                elif val[0] == 1:
                    # edit
                    product_standard_price = self.product_standard_price_ids.browse(val[1])
                    operating_unit_id = product_standard_price.operating_unit_id.id
                    self.with_context(operating_unit_id=operating_unit_id)._set_product_standard_price(val[2]['cost'])
                else:
                    pass

        return res

    def _get_domain_locations(self):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = super(ProductProduct, self)._get_domain_locations()

        if self.env.context.get('operating_unit_id'):
            domain_quant_loc += [('location_id.operating_unit_id', '=', self.env.context.get('operating_unit_id'))]

        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc


class ProductStandardPrice(models.Model):
    _name = 'product.standard.price'

    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        domain=lambda self: [("id", "in", self.env.user.operating_unit_ids.ids)])
    cost = fields.Float('Cost', digits=dp.get_precision('Product Cost Price'))

    @api.constrains('operating_unit_id')
    def _check_operating_unit_id(self):
        if self.operating_unit_id:
            operating_units = self.search(
                [('operating_unit_id', '=', self.operating_unit_id.id),
                 ('product_id', '=', self.product_id.id)]
            )
            if len(operating_units.ids) > 1:
                raise ValidationError(_('[Unique Error] Operating Unit must be unique!'))

    @api.constrains('cost')
    def _check_cost(self):
        if self.cost < 0:
            raise ValidationError(_('Cost Per Unit cannot be negative!'))


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
