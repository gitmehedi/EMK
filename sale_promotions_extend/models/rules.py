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

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools.misc import ustr
import logging
import time
from mx.Tools.mxTools.mxTools import cur_frame

_logger = logging.getLogger(__name__)

#LOGGER = netsvc.Logger()
DEBUG = True
PRODUCT_UOM_ID = 1

ATTRIBUTES = [
    ('amount_untaxed', _('Untaxed Total')),
    #('amount_tax', 'Tax Amount'),
    ('amount_total', 'Total Amount'),
    ('promotional_total', 'Promotional Amount'),
    ('category', 'Product Category in order'),
    ('product', 'Product Code in order'),
    ('prod_qty', 'Product Quantity combination'),
    #('prod_unit_price', 'Product UnitPrice combination'),
    #('prod_sub_total', 'Product SubTotal combination'),
#    ('prod_net_price', 'Product NetPrice combination'),
    #('prod_discount', 'Product Discount combination'),
    #('prod_weight', 'Product Weight combination'),
    ('comp_sub_total', 'Compute sub total of products'),
    ('comp_cat_sub_total', 'Compute sub total of product category'),
    #('comp_sub_total_x', 'Compute sub total excluding products'),
    #('tot_item_qty', 'Total Items Quantity'),
    #('tot_weight', 'Total Weight'),
    #('tot_item_qty', 'Total Items Quantity'),
    ('custom', 'Custom domain expression'),
]

ACTION_TYPES = [
    ('cat_disc_perc', _('Discount % on Product Category')),
    ('prod_disc_perc', _('Discount % on Product')),
    ('cart_disc_fix', _('Fixed amount on Product Category')),
    ('prod_disc_fix', _('Fixed amount on Product')),
    ('prod_sub_disc_perc', _('Discount % on Product Sub Total')),
    ('prod_sub_disc_fix', _('Fixed amount on Product Sub Total')),
    ('cart_disc_perc', _('Discount % on Sub Total')),
    ('cart_disc_fix', _('Fixed amount on Sub Total')),
    ('prod_x_get_y', _('Buy X get Y free'))
]

class PromotionsRules(osv.Model):
    "Promotion Rules"
    _inherit = "promos.rules"
    
    def _check_active_status(self, cr, uid, ids, 
                          name, arg, context=None):
        '''
        This function count the number of sale orders(not in cancelled state)
        that are linked to a particular coupon.
        @param cr: Database Cursor
        @param uid: ID of User
        @param ids: ID of Current record.
        @param name: Name of the field which calls this function.
        @param arg: Any argument(here None).
        @param context: Context(no direct use).
        @return: True or False
        '''
        res = {}
        cur_date = time.strftime("%Y-%m-%d")

        for promotion_rule in self.browse(cr, uid, ids, context=context):            
            #if a start date has been specified
            res[promotion_rule.id] = True

            if promotion_rule.from_date and \
                not (self.promotion_date(
                    cur_date) >= self.promotion_date(promotion_rule.from_date)):
                res[promotion_rule.id] = False

            #If an end date has been specified
            if promotion_rule.to_date and \
                not (self.promotion_date(
                    cur_date) <= self.promotion_date(promotion_rule.to_date)):
                res[promotion_rule.id] = False            
            
        return res
    
    _columns = {
        'active': fields.function(
                    _check_active_status, 
                    store=True, 
                    type='boolean',
                    string='Active',
                    readonly = True,),
        'is_order': fields.boolean('Only Applicable For Order'),
        'group_id':fields.many2one('promotion.groups', 'Group', required=True),
        }
    
    def check_primary_conditions_line(self, cursor, user, promotion_rule, partner_id, date_order, context):
        """
        Checks the conditions for 
            Coupon Code
            Validity Date
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse record sent by calling func. 
        @param context: Context(no direct use).
        """
        #print "-------127--------PromotionsRules----check_primary_conditions_line---------------------"
        partner = self.pool.get('res.partner').browse(cursor, user, partner_id, context)
        #Check if the customer is in the specified partner cats
        if promotion_rule.partner_categories:
            applicable_ids = [
                        category.id \
                          for category in promotion_rule.partner_categories
                            ]
            partner_categories = [
                        category.id \
                            for category in partner.category_id
                                ]
            #print "applicable_ids: ",applicable_ids
            #print "partner_categories: ",partner_categories 
            if not set(applicable_ids).intersection(partner_categories):
                raise Exception("Not applicable to Partner Category")
        #if a start date has been specified
        if promotion_rule.from_date and \
            not (self.promotion_date(
                date_order) >= self.promotion_date(promotion_rule.from_date)):
            raise Exception("Order before start of promotion")

        #If an end date has been specified
        if promotion_rule.to_date and \
            not (self.promotion_date(
                date_order) <= self.promotion_date(promotion_rule.to_date)):
            raise Exception("Order after end of promotion")
        #All tests have succeeded
        return True
    
    def evaluate(self, cursor, user, promotion_rule, order, context=None):
        """
        Evaluates if a promotion is valid
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse Record
        @param order: Browse Record
        @param context: Context(no direct use).
        """
        #print "-----183---------PromotionsRules---------------evaluate-------------------"
        if not context:
            context = {}
        expression_obj = self.pool.get('promos.rules.conditions.exps')
        try:
            self.check_primary_conditions(
                                           cursor, user,
                                           promotion_rule, order,
                                           context)
        except Exception, e:
            if DEBUG:
                logging.error(ustr(e))
            return False
        #print "#Now to the rules checking"
        expected_result = eval(promotion_rule.expected_logic_result)
        logic = promotion_rule.logic
        #print "#Evaluate each expression"
        for expression in promotion_rule.expressions:
            #print "---------203-------------------------------------------------"
            #print expression.serialised_expr
            #if expression.serialised_expr.find('order') < 0:
            #    return False
            result = 'Execution Failed'
            try:
                result = expression_obj.evaluate(cursor, user,
                                             expression, order, context)
                #For and logic, any False is completely false
                if (not (result == expected_result)) and (logic == 'and'):
                    return False
                #For OR logic any True is completely True
                if (result == expected_result) and (logic == 'or'):
                    return True
                #If stop_further is given, then execution stops  if the
                #condition was satisfied
                if (result == expected_result) and expression.stop_further:
                    return True
            except Exception, e:
                raise osv.except_osv("Expression Error", e)
            finally:
                #print "-------------------203----------------------------"
                if DEBUG:
                    if result:
                        logging.info("%s evaluated to %s" % (
                                                   expression.serialised_expr,
                                                   result
                                                   ))
        if logic == 'and':
            #If control comes here for and logic, then all conditions were 
            #satisfied
            return True
        #if control comes here for OR logic, none were satisfied
        return False
    
    def evaluate_line(self, cursor, user, promotion_rule, partner_id, date_order, product, context=None):
        """
        Evaluates if a promotion is valid
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse Record
        @param context: Context(no direct use).
        """
        #print "-----229----------PromotionsRules----evaluate---------------------"
        #print product
        if not context:
            context = {}
        expression_obj = self.pool.get('promos.rules.conditions.exps')
        try:
            self.check_primary_conditions_line(cursor, user, promotion_rule, partner_id, date_order, context)
        except Exception, e:
            if DEBUG:
                logging.error(ustr(e))
            return False
        #Now to the rules checking
        expected_result = eval(promotion_rule.expected_logic_result)
        logic = promotion_rule.logic
        #Evaluate each expression
        for expression in promotion_rule.expressions:
            if expression.serialised_expr.find('order') >= 0:
                return False
            result = 'Execution Failed'
            try:
                result = expression_obj.evaluate_line(cursor, user,
                                             expression, product, context)
                #For and logic, any False is completely false
                if (not (result == expected_result)) and (logic == 'and'):
                    return False
                #For OR logic any True is completely True
                if (result == expected_result) and (logic == 'or'):
                    return True
                #If stop_further is given, then execution stops  if the
                #condition was satisfied
                if (result == expected_result) and expression.stop_further:
                    return True
            except Exception, e:
                raise osv.except_osv("Expression Error", e)
            
        if logic == 'and':
            #If control comes here for and logic, then all conditions were 
            #satisfied
            return True
        #if control comes here for OR logic, none were satisfied
        return False
    
    def execute_actions_line(self, cursor, user, promotion_rule, product, context):
        """
        Executes the actions associated with this rule
        @param cursor: Database Cursor
        @param user: ID of User
        @param promotion_rule: Browse Record
        @param context: Context(no direct use).
        """
        #print "-----281----------PromotionsRules----execute_actions_line---------------------"
        res = []
        action_obj = self.pool.get('promos.rules.actions')
        
        for action in promotion_rule.actions:
            try:
                result =  action_obj.execute_wo_order(cursor, user, action.id, product, context=None)
                if result:
                    res.append(result)
            except Exception, error:
                raise error
        return res
    
    def apply_promotions(self, cursor, user, order_id, context=None):
        """
        Applies promotions
        @param cursor: Database Cursor
        @param user: ID of User
        @param order_id: ID of sale order
        @param context: Context(no direct use).
        """
        #print "--------320-------PromotionsRules----apply_promotions---------------------"
        order = self.pool.get('sale.order').browse(cursor, user,
                                                   order_id, context=context)
        #First Get All the promotion group
        promo_grp_pool = self.pool.get('promotion.groups')
        promo_grps = promo_grp_pool.search(cursor, user,
                                    [('active', '=', True)],
                                    context=context)
        for promo_grp in promo_grp_pool.browse(cursor, user,
                                               promo_grps, context):
            
            active_promos = self.search(cursor, user,
                                        [('active', '=', True),
                                         ('group_id','=',promo_grp.id)],
                                        context=context)
            #print active_promos
            for promotion_rule in self.browse(cursor, user,
                                              active_promos, context):
                order = self.pool.get('sale.order').browse(cursor, user,
                                                   order_id, context=context)
                result = self.evaluate(cursor, user,
                                       promotion_rule, order,
                                       context)
                #If evaluates to true
                #print "-----344------return from evaluate------- ", result
                if result:
                    try:
                        self.execute_actions(cursor, user,
                                         promotion_rule, order_id,
                                         context)
                    except Exception, e:
                        raise osv.except_osv(
                                             "Promotions",
                                             ustr(e)
                                             )
                    #If stop further is true
                    if promotion_rule.stop_further:
                        break
            
            #If stop further is true
            if promo_grp.stop_further:
                return True
        return True
    
    def apply_promotions_line(self, cursor, user, partner_id, date_order, product, context=None):
        """
        Applies promotions
        @param cursor: Database Cursor
        @param user: ID of User
        @param context: Context(no direct use).
        """
        #print "-----301----------PromotionsRules----apply_promotions_line---------------------"
        #print product
        
        #Find out applicable promotions
        result = []
        active_promos = self.search(cursor, user,
                                    [('active', '=', True),('is_order', '=', False)],
                                    context=context)
        #print active_promos
        for promotion_rule in self.browse(cursor, user,
                                          active_promos, context):
            eval_result = self.evaluate_line(cursor, user,
                                   promotion_rule, 
                                   partner_id, 
                                   date_order, 
                                   product, context)
            #print "----317---------------------------------"
            #print eval_result
            #If evaluates to true
            if eval_result:
                try:
                    action_res = self.execute_actions_line(cursor, user,
                                                     promotion_rule, product,
                                                     context)
                    for res in action_res:
                        result.append(res)
                except Exception, e:
                    raise osv.except_osv(
                                         "Promotions",
                                         ustr(e)
                                         )
                #If stop further is true
                if promotion_rule.stop_further:
                    return result
        
        return result
    
PromotionsRules()

class PromotionsRulesConditionsExprs(osv.Model):

    _inherit = 'promos.rules.conditions.exps'
    
    _columns = {
        'attribute':fields.selection(ATTRIBUTES,'Attribute', size=50, required=True),
    }
    
    def on_change(self, cursor, user, ids=None,
                   attribute=None, value=None, context=None):
        
        """
        Set the value field to the format if nothing is there
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of current record.
        @param attribute: attribute sent by caller.
        @param value: Value sent by caller.
        @param context: Context(no direct use).
        """
        res = super(PromotionsRulesConditionsExprs, self).on_change(cursor, user, ids, 
                                                                    attribute, value, context)
        
        #Case 3
        if attribute in [
                         'comp_cat_sub_total',
                         ]:
            return {
                    'value':{
                             'value':"['prod_cat_code','prod_cat_code2']|0.00"
                             }
                    }
        return res
    
    def validate(self, cursor, user, vals, context=None):
        """
        Checks the validity
        @param cursor: Database Cursor
        @param user: ID of User
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        NUMERCIAL_COMPARATORS = ['==', '!=', '<=', '<', '>', '>=']
        ITERATOR_COMPARATORS = ['in', 'not in']
        attribute = vals['attribute']
        comparator = vals['comparator']
        value = vals['value']
        
        #Mismatch 1:
        if attribute in [
                         'comp_cat_sub_total',
                         ] and \
            not comparator in NUMERCIAL_COMPARATORS:
            raise Exception(
                            "Only %s can be used with %s"
                            % ",".join(NUMERCIAL_COMPARATORS), attribute
                            )
        
        #Mismatch 4:
        if attribute in [
                         'comp_cat_sub_total',
                         ]:
            try:
                product_codes_iter, quantity = value.split("|")
                if not (type(eval(product_codes_iter)) in [tuple, list] \
                    and type(eval(quantity)) in [int, long, float]):
                    raise
            except:
                raise Exception(
                        "Value for computed subtotal combination is invalid\n"
                        "Eg for right format is `['code1,code2',..]|120.50`")
        
        res = super(PromotionsRulesConditionsExprs, self).validate(cursor, user, vals, context)
        
        return res
    
    def serialise(self, attribute, comparator, value):
        #print "------349---------------PromotionsRulesConditionsExprs--------------serialise--------------------------------------"
        res = super(PromotionsRulesConditionsExprs, self).serialise(attribute, comparator, value)
        if attribute == 'category':
            return '%s %s categories' % (value,
                                       comparator)
            
        if attribute == 'comp_cat_sub_total':
            product_codes_iter, value = value.split("|")
            return """sum(
                [prod_cat_sub_total.get(cat_code,0) for cat_code in %s]
                ) %s %s""" % (
                               eval(product_codes_iter),
                               comparator,
                               value
                               )
        return res
    
    def evaluate(self, cursor, user,
                 expression, order, context=None):
        """
        Evaluates the expression in given environment
        @param cursor: Database Cursor
        @param user: ID of User
        @param expression: Browse record of expression
        @param context: Context(no direct use).
        @return: True if evaluation succeeded
        """
        #print "------515---------PromotionsRulesConditionsExprs----evaluate---------------------"
        #print order
        categories = [] # List of product Category Code
        products = []   # List of product Codes
        prod_qty = {}   # Dict of product_code:quantity
        prod_unit_price = {}
        prod_sub_total = {}
        prod_cat_sub_total = {}
        prod_discount = {}
        prod_weight = {}
        prod_net_price = {}
        prod_lines = {}
        
        for line in order.order_line:
            product = line.product_id
            cat_code = product.categ_id.code
            categories.append(cat_code)
            product_code = product.code
            products.append(product_code)
            prod_lines[product_code] = product
            prod_qty[product_code] = prod_qty.get(product_code, 0.00) + line.product_uom_qty
        #prod_unit_price[product_code] = prod_unit_price.get(product_code, 0.00) + line.price_unit
            prod_sub_total[product_code] = prod_sub_total.get(product_code, 0.00) + line.price_subtotal
            prod_cat_sub_total[cat_code] = prod_cat_sub_total.get(cat_code, 0.00) + line.price_subtotal
        #prod_discount[product_code] = prod_discount.get(product_code, 0.00) + line.discount
        #prod_weight[product_code] = prod_weight.get(product_code, 0.00) + line.th_weight
        #print "-----546-----", expression.serialised_expr
        #print "-----547-----", eval(expression.serialised_expr)
        return eval(expression.serialised_expr)
    
    def evaluate_line(self, cursor, user,
                 expression, product, context=None):
        """
        Evaluates the expression in given environment
        @param cursor: Database Cursor
        @param user: ID of User
        @param expression: Browse record of expression
        @param context: Context(no direct use).
        @return: True if evaluation succeeded
        """
        #print "----555-----------PromotionsRulesConditionsExprs----evaluate_line---------------------"
        #print product
        categories = [] # List of product Category Code
        products = []   # List of product Codes
        prod_qty = {}   # Dict of product_code:quantity
        prod_unit_price = {}
        prod_sub_total = {}
        prod_discount = {}
        prod_weight = {}
        prod_net_price = {}
        prod_lines = {}
        
        categories.append(product.categ_id.code)
        prod_cat = product.categ_id.code
        product_code = product.code
        products.append(product_code)
        prod_lines[product_code] = product
        #prod_qty[product_code] = prod_qty.get(product_code, 0.00) + line.product_uom_qty
        #prod_unit_price[product_code] = prod_unit_price.get(product_code, 0.00) + line.price_unit
        #prod_sub_total[product_code] = prod_sub_total.get(product_code, 0.00) + line.price_subtotal
        #prod_discount[product_code] = prod_discount.get(product_code, 0.00) + line.discount
        #prod_weight[product_code] = prod_weight.get(product_code, 0.00) + line.th_weight
        #print expression.serialised_expr 
        return eval(expression.serialised_expr)
        
PromotionsRulesConditionsExprs()

class PromotionsRulesActions(osv.Model):
    _inherit = 'promos.rules.actions'
            
    _columns = {
        'action_type':fields.selection(ACTION_TYPES, 'Action', required=True),
        'product_code':fields.char('Code', size=100),
    }
    
    def clear_existing_promotion_lines(self, cursor, user,
                                        order, context=None):
        """
        Deletes existing promotion lines before applying
        @param cursor: Database Cursor
        @param user: ID of User
        @param order: Sale order
        @param context: Context(no direct use).
        """
        #print "-----599---------PromotionsRulesActions---clear_existing_promotion_lines---"
        order_line_obj = self.pool.get('sale.order.line')
        #Delete all promotion lines
        order_line_ids = order_line_obj.search(cursor, user,
                                            [
                                             ('order_id', '=', order.id),
                                             ('promotion_line', '=', True),
                                            ], context=context
                                            )
        if order_line_ids:
            order_line_obj.unlink(cursor, user, order_line_ids, context)
        #Clear discount column
        order_line_ids = order_line_obj.search(cursor, user,
                                            [
                                             ('order_id', '=', order.id),
                                            ], context=context
                                            )
        #if order_line_ids:
            #order_line_obj.write(cursor, user,
            #                     order_line_ids,
            #                     {'discount':0.00},
            #                     context=context)
            
        for line in order_line_obj.browse(cursor, user, order_line_ids, context):
            #print line.product_id.list_price
            order_line_obj.write(cursor, user,
                                 [line.id],
                                 {'discount':0.00,
                                  'price_unit':line.product_id.list_price or 0.0},
                                 context=context)
        return True
    
    def on_change(self, cursor, user, ids=None,
                   action_type=None, product_code=None,
                   arguments=None, context=None):
        """
        Sets the arguments as templates according to action_type
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of current record
        @param action_type: type of action to be taken
        @product_code: Product on which action will be taken.
                (Only in cases when attribute in expression is product.)
        @param arguments: Values that will be used in implementing of actions
        @param context: Context(no direct use).
        """
        if action_type in [
                           'cart_disc_perc',
                           'cart_disc_fix',
                           ] :
            return {
                    'value':{
                             'product_code':"'prod_cat_code'",
                             'arguments':"0.00",
                             }
                    }
        res = super(PromotionsRulesActions, self).on_change(cursor, user, ids,
                                                            action_type, product_code,
                                                            arguments, context)
        return res
    
    def execute_wo_order(self, cursor, user, action_id, product, context=None):
        """
        Executes the action into the order
        @param cursor: Database Cursor
        @param user: ID of User
        @param action_id: Action to be taken on sale order
        @param context: Context(no direct use).
        """
        #print "-----447----------PromotionsRulesActions----execute_wo_order---------------------"
        order = False
        action = self.browse(cursor, user, action_id, context)
        method_name = 'action_' + action.action_type
        return getattr(self, method_name).__call__(cursor, user, action,
                                                   order, product, context)
    
    def execute(self, cursor, user, action_id,
                                   order, context=None):
        """
        Executes the action into the order
        @param cursor: Database Cursor
        @param user: ID of User
        @param action_id: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        #print "-----663----------PromotionsRulesActions----execute---------------------"
        action = self.browse(cursor, user, action_id, context)
        method_name = 'action_' + action.action_type
        return getattr(self, method_name).__call__(cursor, user, action,
                                                   order, context)
    
    def action_cart_disc_perc(self, cr, uid, action, order, context=None):
        #print "----472-----------PromotionsRulesActions----action_cart_disc_perc---------------------"
        if  float(action.arguments) > 0.0 and float(action.arguments) < 100.0:
            line_pool = self.pool.get('sale.order.line')
            for line in order.order_line:
                up = line.price_unit
                up = up - (up/float(action.arguments))
                line_pool.write(cr, uid, [line.id], {'price_unit':up}, context)
    
    def action_cart_disc_fix(self, cr, uid, action, order, product, context=None):
        print "------703---------PromotionsRulesActions----action_cart_disc_fix---------------------"
        """
        Action for 'Fix Discount on Product Category'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        if product:
            if product.categ_id.code == eval(action.product_code):
                return action.arguments + 'F'
            
        if order:
            order_line_obj = self.pool.get('sale.order.line')
            for order_line in order.order_line:
                if order_line.product_id.product_tmpl_id.categ_id.code == eval(action.product_code):
                    #discount = order_line.discount + eval(action.arguments)
                    current_unit_price = order_line.price_unit
                    new_unit_price = current_unit_price - eval(action.arguments)
                    order_line_obj.write(cr,
                                         uid,
                                         order_line.id,
                                         {
                                          'price_unit':new_unit_price,
                                          },
                                         context
                                         )
        
    
    def action_cat_disc_perc(self, cursor, user,
                               action, order, product, context=None):
        #print "action_cat_disc_perc"
        """
        Action for 'Discount % on Product Category'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        #print "-----753----------PromotionsRulesActions----action_cat_disc_perc---------------------"
        #print order
        #print product
        if product:
            if product.categ_id.code == eval(action.product_code):
                return action.arguments
        
        if order:
            order_line_obj = self.pool.get('sale.order.line')
            for order_line in order.order_line:
                if order_line.product_id.product_tmpl_id.categ_id.code == eval(action.product_code):
                    #discount = order_line.discount + eval(action.arguments)
                    current_unit_price = order_line.price_unit
                    new_unit_price = current_unit_price - (current_unit_price*eval(action.arguments)/100)
                    order_line_obj.write(cursor,
                                         user,
                                         order_line.id,
                                         {
                                          'price_unit':new_unit_price,
                                          },
                                         context
                                         )

    def action_prod_disc_fix(self, cr, uid,
                              action, order, product, context=None):
        
        """
        Action for 'Discount % on Product'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        #print "-----778----------PromotionsRulesActions----action_prod_disc_fix---------------------"
        if product:
            if product.default_code == eval(action.product_code):
                return action.arguments + 'F'
            
        if order:
            order_line_obj = self.pool.get('sale.order.line')
            for order_line in order.order_line:
                if order_line.product_id.default_code == eval(action.product_code):
                    #discount = order_line.discount + eval(action.arguments)
                    current_unit_price = order_line.price_unit
                    new_unit_price = current_unit_price - eval(action.arguments)
                    order_line_obj.write(cr,
                                         uid,
                                         order_line.id,
                                         {
                                          'price_unit':new_unit_price,
                                          },
                                         context
                                         )
        
    def action_prod_disc_perc(self, cr, uid,
                               action, order, product, context=None):
        """
        Action for 'Discount % on Product'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        #print "-----809----------PromotionsRulesActions----action_prod_disc_perc---------------------"
        #print order
        #print product
        if product:
            if product.default_code == eval(action.product_code):
                return action.arguments
            
        if order:
            order_line_obj = self.pool.get('sale.order.line')
            for order_line in order.order_line:
                if order_line.product_id.default_code == eval(action.product_code):
                    #discount = order_line.discount + eval(action.arguments)
                    current_unit_price = order_line.price_unit
                    dis_amount = current_unit_price * eval(action.arguments) / 100
                    new_unit_price = current_unit_price - dis_amount
                    order_line_obj.write(cr,
                                         uid,
                                         order_line.id,
                                         {
                                          'price_unit':new_unit_price,
                                          },
                                         context
                                         )
            
        
            
    def action_special_disc(self, cursor, user,
                               order, context=None):
        """
        'Special Discount % on Sub Total'
        @param cursor: Database Cursor
        @param user: ID of User
        @param action: Action to be taken on sale order
        @param order: sale order
        @param context: Context(no direct use).
        """
        order_line_obj = self.pool.get('sale.order.line')
        if not order.special_discount_type:
            return True
        if order.special_discount_type == 'fix':
            return order_line_obj.create(cursor,
                                      user,
                                      {
                          'order_id':order.id,
                          'name':'Special Discount',
                          'price_unit':-order.special_discount_value,
                          'product_uom_qty':1,
                          'promotion_line':True,
                          'product_uom':PRODUCT_UOM_ID
                                      },
                                      context
                                      )
        if order.special_discount_type == 'perc':
            return order_line_obj.create(cursor,
                                      user,
                                      {
                          'order_id':order.id,
                          'name':'Special Discount',
                          'price_unit':-(order.amount_untaxed \
                                        * order.special_discount_value / 100),
                          'product_uom_qty':1,
                          'promotion_line':True,
                          'product_uom':PRODUCT_UOM_ID
                                      },
                                      context
                                      )

PromotionsRulesActions()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: