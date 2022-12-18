from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'product.sales.pricelist'

    is_corporate = fields.Boolean(string='Is Corporate', compute="_compute_company_id_is_retail_or_corporate")
    is_retailer = fields.Boolean(string='Is Retailer', compute="_compute_company_id_is_retail_or_corporate")

    @api.multi
    @api.depends('company_id')
    def _compute_company_id_is_retail_or_corporate(self):
        for rec in self:
            rec.is_corporate = False
            rec.is_retailer = False

            for type in rec.company_id.customer_types:
                if type.is_corporate:
                    rec.is_corporate = True
                if type.is_retail:
                    rec.is_retailer = True

    # corporate customer
    # commission
    corporate_commission_per_unit = fields.Float(string='Per Unit Amt.')
    corporate_commission_tolerable = fields.Float(string='Tolerable (+/-)')

    # refund
    corporate_refund_per_unit = fields.Float(string='Per Unit Amt.')
    corporate_refund_tolerable = fields.Float(string='Tolerable (+/-)')

    # dealer customer
    dealer_commission_applicable = fields.Boolean(string='Commission Applicable', required=False)
    dealer_refund_applicable = fields.Boolean(string='Refund Applicable', required=False)
