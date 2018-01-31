from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char(string="Internal Reference", required=False)

    @api.constrains('default_code')
    def _unique_name(self):
        name = self.search([('default_code', '=ilike', self.default_code)])
        if len(name) > 1:
            raise Warning('[{0}] name already in your list, please think another.'.format(self.default_code))


class ProductTemplateProduct(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char(string="Internal Reference", required=False)

    @api.constrains('default_code')
    def _unique_name(self):
        name = self.search([('default_code', '=ilike', self.default_code)])
        if len(name) > 1:
            raise Warning('[{0}] name already in your list, please think another.'.format(self.default_code))