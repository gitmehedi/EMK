from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit='res.partner'

    supplier_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], string='Supplier Type')

    is_cnf = fields.Boolean(string='Is a C&F Agent')

    ntn_no = fields.Char('NTN No', size=20)
    gst_no = fields.Char('GST No', size=20)
    iec_no = fields.Char('IEC No', size=20)

    """ Relational Fields """
    supplier_category_id = fields.Many2one('supplier.category',string='Supplier Category')
    sector_id = fields.Many2one('res.partner.category',string='Sector')
