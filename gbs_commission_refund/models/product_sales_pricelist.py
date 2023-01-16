from collections import defaultdict
import json
import time

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from lxml import etree


class SaleOrderApprovePricelist(models.Model):
    _inherit = 'product.sale.history.line'

    # commission
    corporate_commission_per_unit = fields.Float(string='Per Unit Amt.')
    corporate_commission_tolerable = fields.Float(string='Tolerable (+/-)')

    # refund
    corporate_refund_per_unit = fields.Float(string='Per Unit Amt.')
    corporate_refund_tolerable = fields.Float(string='Tolerable (+/-)')

    # commission/refund for slab wise claim
    dealer_commission_applicable = fields.Boolean(string='Commission Applicable')
    dealer_refund_applicable = fields.Boolean(string='Refund Applicable')

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrderApprovePricelist, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        company = self.env.user.company_id
        textbox_config = self.env['commission.configuration'].search([
            ('process', '=', 'textbox'),
            ('customer_type', 'in', company.customer_types.ids or []),
            ('functional_unit', 'in', company.branch_ids.ids or [])
        ], limit=1)

        checkbox_config = self.env['commission.configuration'].search([
            ('process', '=', 'checkbox'),
            ('customer_type', 'in', company.customer_types.ids or []),
            ('functional_unit', 'in', company.branch_ids.ids or [])
        ], limit=1)

        if view_type == 'form':
            doc = etree.XML(result['arch'])
            if (not textbox_config.show_packing_mode and not checkbox_config.show_packing_mode) and view_type == 'form':
                for field in doc.xpath("//field[@name='product_package_mode']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if not textbox_config:
                for field in doc.xpath("//group[@name='corporate_commission_refund_group']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if not checkbox_config:
                for field in doc.xpath("//group[@name='dealer_commission_refund_group']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            result['arch'] = etree.tostring(doc)

        elif view_type == 'tree':
            doc = etree.XML(result['arch'])
            if not textbox_config:
                fields_to_be_hidden = ['corporate_commission_per_unit', 'corporate_commission_tolerable', 'corporate_refund_per_unit', 'corporate_refund_tolerable']
                for f in fields_to_be_hidden:
                    for field in doc.xpath("//field[@name='%s']" % f):
                        modifiers = json.loads(field.get('modifiers', '{}'))
                        modifiers['invisible'] = True
                        modifiers['tree_invisible'] = True
                        modifiers['column_invisible'] = True
                        field.set('modifiers', json.dumps(modifiers))

            if not checkbox_config:
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

    @api.model
    def pull_automation(self):
        current_date = time.strftime("%d/%m/%Y")
        vals = {}

        price_list_pool = self.env['product.sales.pricelist'].search(
            [('state', '=', 'validate'), ('effective_date', '<=', current_date), ('is_process', '=', 0)],
            order='effective_date ASC',
        )

        for price_pool in price_list_pool:
            price_history_pool = self.env['product.sale.history.line'].search([
                ('product_id', '=', price_pool.product_id.ids),
                ('currency_id', '=', price_pool.currency_id.id),
                ('product_package_mode', '=', price_pool.product_package_mode.id),
                ('uom_id', '=', price_pool.uom_id.id)
            ])

            if not price_history_pool:
                vals['product_id'] = price_pool.product_id.id
                vals['list_price'] = price_pool.list_price
                vals['new_price'] = price_pool.new_price
                vals['sale_price_history_id'] = price_pool.id
                vals['approve_price_date'] = price_pool.effective_date
                vals['currency_id'] = price_pool.currency_id.id
                vals['product_package_mode'] = price_pool.product_package_mode.id
                vals['uom_id'] = price_pool.uom_id.id
                vals['category_id'] = price_pool.uom_id.category_id.id
                vals['discount'] = price_pool.discount

                # commission/refund values
                vals['corporate_commission_per_unit'] = price_pool.corporate_commission_per_unit
                vals['corporate_commission_tolerable'] = price_pool.corporate_commission_tolerable
                vals['corporate_refund_per_unit'] = price_pool.corporate_refund_per_unit
                vals['corporate_refund_tolerable'] = price_pool.corporate_refund_tolerable
                vals['dealer_commission_applicable'] = price_pool.dealer_commission_applicable
                vals['dealer_refund_applicable'] = price_pool.dealer_refund_applicable

                # create new record
                price_history_pool.create(vals)
            else:
                write_vals = {
                    'corporate_commission_per_unit': price_pool.corporate_commission_per_unit,
                    'corporate_commission_tolerable': price_pool.corporate_commission_tolerable,
                    'corporate_refund_per_unit': price_pool.corporate_refund_per_unit,
                    'corporate_refund_tolerable': price_pool.corporate_refund_tolerable,
                    'dealer_commission_applicable': price_pool.dealer_commission_applicable,
                    'dealer_refund_applicable': price_pool.dealer_refund_applicable
                }

                # commission/refund values
                price_history_pool.write(write_vals)

        res = super(SaleOrderApprovePricelist, self).pull_automation()
        return res


class SaleOrderPricelist(models.Model):
    _inherit = 'product.sales.pricelist'

    is_corporate = fields.Boolean(
        string='Is Corporate',
        compute="_compute_company_id_is_retail_or_corporate"
    )
    is_retailer = fields.Boolean(
        string='Is Retailer',
        compute="_compute_company_id_is_retail_or_corporate"
    )

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
    dealer_commission_applicable = fields.Boolean(string='Commission Applicable')
    dealer_refund_applicable = fields.Boolean(string='Refund Applicable')

    @api.onchange('corporate_commission_per_unit', 'corporate_commission_tolerable')
    def _difference_commission_amount(self):
        for rec in self:
            if rec.corporate_commission_per_unit < 0:
                rec.corporate_commission_per_unit *= -1
            if rec.corporate_commission_tolerable < 0:
                rec.corporate_commission_tolerable *= -1

    @api.onchange('corporate_refund_per_unit', 'corporate_refund_tolerable')
    def _difference_refund_amount(self):
        for rec in self:
            if rec.corporate_refund_per_unit < 0:
                rec.corporate_refund_per_unit *= -1
            if rec.corporate_refund_tolerable < 0:
                rec.corporate_refund_tolerable *= -1

    @api.model
    def create(self, values):
        if values.get('corporate_commission_tolerable', 0) > values.get('corporate_commission_per_unit', 0):
            raise UserError(_("Commission tolerable can't be larger than actual."))

        if values.get('corporate_refund_tolerable', 0) > values.get('corporate_refund_per_unit', 0):
            raise UserError(_("Refund tolerable can't be larger than actual."))

        return super(SaleOrderPricelist, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('corporate_commission_tolerable', self.corporate_commission_tolerable) > values.get('corporate_commission_per_unit', self.corporate_commission_per_unit):
            raise UserError(_("Commission tolerable can't be larger than actual."))

        if values.get('corporate_refund_tolerable', self.corporate_refund_tolerable) > values.get('corporate_refund_per_unit', self.corporate_refund_per_unit):
            raise UserError(_("Refund tolerable can't be larger than actual."))

        return super(SaleOrderPricelist, self).write(values)

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrderPricelist, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        company = self.env.user.company_id
        textbox_config = self.env['commission.configuration'].search([
            ('process', '=', 'textbox'),
            ('customer_type', 'in', company.customer_types.ids or []),
            ('functional_unit', 'in', company.branch_ids.ids or [])
        ], limit=1)

        checkbox_config = self.env['commission.configuration'].search([
            ('process', '=', 'checkbox'),
            ('customer_type', 'in', company.customer_types.ids or []),
            ('functional_unit', 'in', company.branch_ids.ids or [])
        ], limit=1)

        if view_type == 'form':
            doc = etree.XML(result['arch'])
            if (not textbox_config.show_packing_mode and not checkbox_config.show_packing_mode) and view_type == 'form':
                for field in doc.xpath("//field[@name='product_package_mode']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if not textbox_config:
                for field in doc.xpath("//group[@name='corporate_commission_refund_group']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            if not checkbox_config:
                for field in doc.xpath("//group[@name='dealer_commission_refund_group']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

            result['arch'] = etree.tostring(doc)

        elif view_type == 'tree':
            doc = etree.XML(result['arch'])
            if not textbox_config:
                fields_to_be_hidden = ['corporate_commission_per_unit', 'corporate_commission_tolerable', 'corporate_refund_per_unit', 'corporate_refund_tolerable']
                for f in fields_to_be_hidden:
                    for field in doc.xpath("//field[@name='%s']" % f):
                        modifiers = json.loads(field.get('modifiers', '{}'))
                        modifiers['invisible'] = True
                        modifiers['tree_invisible'] = True
                        modifiers['column_invisible'] = True
                        field.set('modifiers', json.dumps(modifiers))

            if not checkbox_config:
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
