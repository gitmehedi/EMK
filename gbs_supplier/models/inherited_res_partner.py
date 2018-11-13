from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit='res.partner'

    supplier_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], string='Supplier Type')
    is_cnf = fields.Boolean(string='Is C&F Agent')

    """ Relational Fields """
    supplier_category_id = fields.Many2one('supplier.category',string='Supplier Category')
