from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('rent', 'Rent')])


class ProductProductWizard(models.TransientModel):
    _inherit = 'product.product.wizard'

    type = fields.Selection(selection_add=[('rent', 'Rent')])


class HistoryProductProduct(models.Model):
    _inherit = 'history.product.product'

    type = fields.Selection(selection_add=[('rent', 'Rent')])
