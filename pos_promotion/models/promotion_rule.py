from openerp import models, fields, api, exceptions, osv

import sys, json


try:
    # Backward compatible
    from sets import Set as set
except:
    pass

import logging
from openerp.osv import osv, fields
from openerp import models, fields
from openerp.tools.misc import ustr
from openerp.tools.translate import _

# Get the logger
_logger = logging.getLogger(__name__)
# LOGGER = netsvc.Logger()
DEBUG = True
PRODUCT_UOM_ID = 1

ATTRIBUTES = [

    ('amount_total', 'Total Amount(Excluded Tax)'),
    ('amount_include_total', 'Total Amount(Included Tax)'),

    ('prod_qty', 'Product Quantity combination'),
    ('prod_unit_price', 'Product UnitPrice combination'),

]

COMPARATORS = [
    ('==', _('equals')),
    ('!=', _('not equal to')),
    ('>', _('greater than')),
    ('>=', _('greater than or equal to')),

]

ACTION_TYPES = [
    ('cat_disc_perc', _('Discount % on Product Category')),
    ('prod_disc_perc', _('Discount % on Product')),
    ('cat_disc_fix', _('Fixed amount on Product Category')),
    ('prod_disc_fix', _('Fixed amount on Product')),
    ('prod_sub_disc_perc', _('Discount % on Product Sub Total')),
    ('prod_sub_disc_fix', _('Fixed amount on Product Sub Total')),
    ('cart_disc_perc', _('Discount % on Sub Total')),
    ('cart_disc_fix', _('Fixed amount on Sub Total')),
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
    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
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

    sequence = fields.Integer('Sequence', required=True)
    action_type = fields.Selection(ACTION_TYPES, 'Action', required=True)
    product_code = fields.Char('Product Code', size=100)
    arguments = fields.Char('Arguments', size=100, )
    promotion = fields.Many2one('promos.rules', 'Promotion')

