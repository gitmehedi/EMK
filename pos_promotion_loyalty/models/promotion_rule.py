from openerp import models, fields, api, exceptions, osv
from openerp.addons.helper import validator
import sys, json

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

try:
    # Backward compatible
    from sets import Set as set
except:
    pass

import logging
from openerp.osv import osv, fields
from openerp import models, fields
from openerp.tools.misc import ustr
# from openerp import netsvc
from openerp.tools.translate import _

# Get the logger
_logger = logging.getLogger(__name__)
# LOGGER = netsvc.Logger()
DEBUG = True
PRODUCT_UOM_ID = 1

ATTRIBUTES = [
    # ('amount_untaxed', _('Untaxed Total')),
    # ('amount_tax', 'Tax Amount'),
    ('amount_total', 'Total Amount(Excluded Tax)'),
    ('amount_include_total', 'Total Amount(Included Tax)'),
    # ('promotional_total', 'Promotional Amount'),
    # ('category', 'Product Category in order'),
    # ('product', 'Product Code in order'),
    ('prod_qty', 'Product Quantity combination'),
    ('prod_unit_price', 'Product UnitPrice combination'),
    # ('prod_sub_total', 'Product SubTotal combination'),
    #    ('prod_net_price', 'Product NetPrice combination'),
    # ('comp_sub_total', 'Compute sub total of products'),
    # ('comp_cat_sub_total', 'Compute sub total of product category'),
    # ('comp_sub_total_x', 'Compute sub total excluding products'),
    # ('tot_item_qty', 'Total Items Quantity'),
    # ('tot_weight', 'Total Weight'),
    # ('tot_item_qty', 'Total Items Quantity'),
    # ('custom', 'Custom domain expression'),
]

COMPARATORS = [
    ('==', _('equals')),
    ('!=', _('not equal to')),
    ('>', _('greater than')),
    ('>=', _('greater than or equal to')),
    # ('<', _('less than')),
    # ('<=', _('less than or equal to')),
    # ('in', _('is in')),
    # ('not in', _('is not in')),
]

ACTION_TYPES = [
    ('cat_disc_perc', _('Discount % on Product Category')),
    ('prod_disc_perc', _('Discount % on Product')),
    ('cat_disc_fix', _('Fixed amount on Product Category')),
    ('prod_disc_fix', _('Fixed amount on Product')),
    ('prod_sub_disc_perc', _('Discount % on Product Sub Total')),
    ('prod_sub_disc_fix', _('Fixed amount on Product Sub Total')),
    ('cart_disc_perc', _('Discount % on Sub Total(excluding tax)')),
    ('cart_disc_fix', _('Fixed amount on Sub Total(excluding tax)')),
    ('cart_disc_tax_perc', _('Discount % on Sub Total(including tax)')),
    ('cart_disc_tax_fix', _('Fixed amount on Sub Total(including tax)')),
    # ('prod_x_get_y', _('Buy X get Y free'))
]


class PromotionGroups(models.Model):
    # TODO: when to use group promotion
    _name = "promotion.groups"
    active = fields.Boolean('Active')
    stop_further = fields.Boolean('Stop Checks', help="Stops further promotion group being checked")
    name = fields.Char('Group', required=True)
    sequence = fields.Integer('Sequence')


class PromotionsRules(models.Model):
    _name = "promos.rules"

    name = fields.Char(string="Rule Name", required=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer(string="Sequence")
    uses_per_coupon = fields.Integer(string="Uses Per Coupon")
    coupon_code = fields.Char()
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="Start Date")
    stop_further = fields.Boolean()
    logic = fields.Selection([('and', 'All'), ('or', 'Any')], default='and', required=True)
    active = fields.Boolean()
    uses_per_partner = fields.Integer(string="Uses Per Partner")

    expected_logic_result = fields.Selection([('True', 'True'), ('False', 'False')], string="Output", required=True,
                                             default='True')

    is_order = fields.Boolean()
    group_id = fields.Many2one('promotion.groups')
    actions = fields.One2many('promos.rules.actions', 'promotion')
    expressions = fields.One2many('promos.rules.conditions.exps', 'promotion')
    partner_categories = fields.Many2many('res.partner.category')


class PromotionsRulesConditionsExprs(osv.Model):
    _name = 'promos.rules.conditions.exps'

    sequence = fields.Integer(string='Sequence')
    attribute = fields.Selection(ATTRIBUTES, string='Attribute', size=50, required=True)
    comparator = fields.Selection(COMPARATORS, string='Comparator', required=True, default='==')
    value = fields.Char('Value', size=255)
    price = fields.Float(string='Price')
    quantity = fields.Integer(string='Quantity')
    serialised_expr = fields.Char(string='Expression', size=255)
    promotion = fields.Many2one('promos.rules', string='Promotion')
    stop_further = fields.Boolean(string='Stop further checks', default='1')


class PromotionsRulesActions(osv.Model):
    _name = 'promos.rules.actions'
    #     _rec_name = 'action_type'

    sequence = fields.Integer('Sequence', required=True)
    action_type = fields.Selection(ACTION_TYPES, 'Action', required=True)
    product_code = fields.Char('Product Code', size=100)
    arguments = fields.Char('Arguments', size=100, )
    promotion = fields.Many2one('promos.rules', 'Promotion')

   