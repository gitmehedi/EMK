from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = 'stock.location'

    can_loan_request = fields.Boolean('Can request for Item Loan ?')