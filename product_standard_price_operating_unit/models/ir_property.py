# import of odoo
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class Property(models.Model):
    _inherit = 'ir.property'

    @api.model
    def get_multi(self, name, model, ids):
        """
            :param string name: field name
            :param string model: model name
            :param list ids: record ids
        """
        res = super(Property, self).get_multi(name, model, ids)

        # operating unit wise standard_price(Cost Per Unit)
        if name == 'standard_price' and model == 'product.product' and ids:
            operating_unit_id = self.env.context.get('operating_unit_id')
            if operating_unit_id:
                for product_id in ids:
                    product_standard_price = self.env['product.standard.price'].search(
                        [('product_id', '=', product_id),
                         ('operating_unit_id', '=', operating_unit_id)]
                    )

                    if product_standard_price:
                        res[product_id] = product_standard_price.cost
                    else:
                        res[product_id] = 0.0
            else:
                _logger.info("SAMUDA-CUSTOM-ERROR: [GET] operating unit not found in the context")
                # for testing purpose
                # if not self.env.context.get('from_menu'):
                #     raise UserError(_('[GET] GET ERROR.\nOperating Unit not found in the context.'))

        return res

    @api.model
    def set_multi(self, name, model, values, default_value=None):
        """
            :param string name: field name
            :param string model: model name
            :param dictionary values: key=product_id, val=cost
            :param float default_value: default cost
        """
        # execute the parent class method
        super(Property, self).set_multi(name, model, values, default_value)

        # operating unit wise standard_price(Cost Per Unit)
        if name == 'standard_price' and model == 'product.product' and values:
            operating_unit_id = self.env.context.get('operating_unit_id')
            if operating_unit_id:
                # Modify existing records if exist, else create new records
                for product_id, cost in values.items():
                    product_standard_price = self.env['product.standard.price'].search(
                        [('product_id', '=', product_id),
                         ('operating_unit_id', '=', operating_unit_id)]
                    )

                    if product_standard_price:
                        if product_standard_price.cost != cost:
                            product_standard_price.write({'cost': cost})
                    else:
                        self.env['product.standard.price'].create({
                            'product_id': product_id,
                            'operating_unit_id': operating_unit_id,
                            'cost': cost
                        })
            else:
                _logger.info("SAMUDA-CUSTOM-ERROR: [CREATE, UPDATE] operating unit not found in the context")
                # for testing purpose
                # if not self.env.context.get('from_menu'):
                #     raise UserError(_('[CREATE, UPDATE] CREATE OR UPDATE ERROR.\nOperating Unit not found in the context.'))
