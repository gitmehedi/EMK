from datetime import datetime
from openerp import api, models, fields


class ProductRequisitionTemplateModel(models.Model):
    _name = 'product.requisition.template'
    _description = 'Product Requisition Template.'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    name = fields.Char(string="Template Name", required=True)
    status = fields.Boolean(string="Status", default=True)

    """ Relational Filds """
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=False,
                                        default=_default_operating_unit)
    line_ids = fields.One2many('product.requisition.template.line', 'template_id')


class ProductRequisitionTemplateLineModel(models.Model):
    _name = 'product.requisition.template.line'
    _description = 'Product Requisition Template Line.'
    _order = "category_id ASC, product_id ASC"

    """ Relational Filds """
    product_id = fields.Many2one('product.product', string='Product Name', required=True)
    category_id = fields.Many2one('product.category', related="product_id.categ_id", string='Category Name', store=True,
                                  readonly=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string='UoM', readonly=True, store=True)
    template_id = fields.Many2one('product.requisition.template', ondelete='cascade')
