from collections import defaultdict
import json

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from lxml import etree


class SaleOrderPricelist(models.Model):
    _inherit = 'product.sales.pricelist'

    is_corporate = fields.Boolean(string='Is Corporate', compute="_compute_company_id_is_retail_or_corporate")
    is_retailer = fields.Boolean(string='Is Retailer', compute="_compute_company_id_is_retail_or_corporate")

    @api.multi
    @api.depends('company_id')
    def _compute_company_id_is_retail_or_corporate(self):
        for rec in self:
            rec.is_corporate = False
            rec.is_retailer = False

            for c_type in rec.company_id.customer_types:
                if c_type.is_corporate:
                    rec.is_corporate = True
                if c_type.is_retail:
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

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrderPricelist, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            company = self.env.user.company_id
            config = self.env['commission.configuration'].search([('customer_type', 'in', company.customer_types.ids or []), ('functional_unit', 'in', company.branch_ids.ids or [])], limit=1)

            doc = etree.XML(result['arch'])
            if not config.show_packing_mode and view_type == 'form':
                for field in doc.xpath("//field[@name='product_package_mode']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if config.process != 'textbox':
                for field in doc.xpath("//group[@name='corporate_commission_refund_group']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if config.process != 'checkbox':
                for field in doc.xpath("//group[@name='dealer_commission_refund_group']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            result['arch'] = etree.tostring(doc)

        elif view_type == 'tree':
            company = self.env.user.company_id
            config = self.env['commission.configuration'].search([('customer_type', 'in', company.customer_types.ids or []), ('functional_unit', 'in', company.branch_ids.ids or [])], limit=1)

            doc = etree.XML(result['arch'])
            if config.process != 'textbox':
                fields_to_be_hidden = ['corporate_commission_per_unit', 'corporate_commission_tolerable', 'corporate_refund_per_unit', 'corporate_refund_tolerable']
                for f in fields_to_be_hidden:
                    for field in doc.xpath("//field[@name='%s']" % f):
                        modifiers = json.loads(field.get('modifiers', '{}'))
                        modifiers['invisible'] = True
                        modifiers['tree_invisible'] = True
                        modifiers['column_invisible'] = True
                        field.set('modifiers', json.dumps(modifiers))

            if config.process != 'checkbox':
                fields_to_be_hidden = ['dealer_commission_applicable', 'dealer_refund_applicable']
                for f in fields_to_be_hidden:
                    for field in doc.xpath("//field[@name='%s']" % f):
                        modifiers = json.loads(field.get('modifiers', '{}'))
                        modifiers['invisible'] = True
                        modifiers['tree_invisible'] = True
                        modifiers['column_invisible'] = True
                        field.set('modifiers', json.dumps(modifiers))

            result['arch'] = etree.tostring(doc)

        return result
