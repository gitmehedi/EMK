from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

from datetime import date

import datetime
import time


class SalePriceChange(models.Model):
    _name = 'product.sales.pricelist'
    _description = "Product Sales Pricelist"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'product_id'
    _order = "effective_date,id desc"

    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)],
                                 states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                         'validate2': [('readonly', True)],
                                         'validate': [('readonly', True)]}, string='Product', required=True)

    list_price = fields.Float(string='Old Price', compute='compute_list_price', readonly=True, store=True,digits=dp.get_precision('Product Price'))

    new_price = fields.Float(string='New Price',
                             states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                     'validate2': [('readonly', True)],
                                     'validate': [('readonly', True)]}, required=True, digits=dp.get_precision('Product Price'))
    product_package_mode = fields.Many2one('product.packaging.mode', string='Packaging Mode',
                                           states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                                   'validate2': [('readonly', True)],
                                                   'validate': [('readonly', True)]}, required=True)
    uom_id = fields.Many2one('product.uom', string="UoM", domain=[('category_id', '=', 2)],
                             states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                     'validate2': [('readonly', True)],
                                     'validate': [('readonly', True)]}, required=True)
    category_id = fields.Many2one(string='UoM Category', related="uom_id.category_id", store=True)
    request_date = fields.Date(string='Request Date', default=datetime.datetime.now(),
                               states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                       'validate2': [('readonly', True)],
                                       'validate': [('readonly', True)]}, readonly=True)
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user,
                                   readonly=True)

    approver1_id = fields.Many2one('res.users', string='First Approval', readonly=True)
    approver2_id = fields.Many2one('res.users', string='Second Approval', readonly=True)

    approver1_date = fields.Date(string='First Approval Date',
                                 states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                         'validate2': [('readonly', True)],
                                         'validate': [('readonly', True)]}, readonly=True)
    approver2_date = fields.Date(string='Second Approval Date',
                                 states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                         'validate2': [('readonly', True)],
                                         'validate': [('readonly', True)]}, readonly=True)
    effective_date = fields.Date(string='Effective Date',
                                 states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                         'validate2': [('readonly', True)],
                                         'validate': [('readonly', True)]}, required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Sales Approval'),
        ('validate2', 'Accounts Approval'),
        ('validate1', 'CXO Approval'),
        ('validate', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True, track_visibility='onchange', copy=False, default='draft')

    currency_id = fields.Many2one('res.currency', string="Currency",
                                  states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate2': [('readonly', True)],
                                          'validate': [('readonly', True)]}, required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'product_sales_pricelist'), required=True)

    discount = fields.Float(string='Max Discount Limit',
                            states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate2': [('readonly', True)],'validate2': [('readonly', True)],
                                    'validate': [('readonly', True)]}, )

    is_process = fields.Integer(string='Is Process', default=0)

    #-------------------------
    # country_id = fields.Many2one('res.country', string='Country', states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate2': [('readonly', True)],'validate2': [('readonly', True)],
    #                                 'validate': [('readonly', True)]},)
    #
    # terms_setup_id = fields.Many2one('terms.setup', string='Payment Days', states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate2': [('readonly', True)],'validate2': [('readonly', True)],
    #                                 'validate': [('readonly', True)]})
    #
    # freight_mode = fields.Selection([
    #     ('fob', 'FOB'),
    #     ('c&f', 'C&F')
    # ], string='Freight Mode',default='fob', states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate2': [('readonly', True)],'validate2': [('readonly', True)],
    #                                 'validate': [('readonly', True)]})




    @api.constrains('discount')
    def _max_discount_limit_validation(self):
        if self.discount < 0.00:
            raise ValidationError('Max Discount Limit can not be Negative')

        if self.discount > self.new_price:
            raise ValidationError('Max Discount Limit can not be greater than New Price')


    def action_sales_head(self):
        self.state = 'validate2'

    @api.constrains('new_price')
    def check_new_price(self):
        if self.new_price < 0.00:
            raise ValidationError('New Price can not be Negative')

    @api.constrains('effective_date')
    def check_effective_date(self):
        if self.request_date > self.effective_date:
            raise ValidationError('Effective date must be after request date')

    def price_change(self):
        if self.product_id:
            product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])

            if product_pool:
                for ps in product_pool:
                    self.currency_id = ps.currency_id.id

                count = self.search_count(
                    [('product_id', '=', self.product_id.id), ('currency_id', '=', self.currency_id.id),
                     ('state', '=', 'validate')])

                if count > 0:
                    price_change_pool = \
                        self.env['product.sales.pricelist'].search([('product_id', '=', self.product_id.id),
                                                                    ('currency_id', '=', self.currency_id.id),
                                                                    ('state', '=', 'validate')], order='id desc')[0]
                    self.list_price = price_change_pool.new_price
                    self.uom_id = price_change_pool.uom_id
                else:
                    self.list_price = product_pool.list_price

        else:
            self.list_price = 0.00

    @api.onchange('product_id')
    def _onchange_product_form(self):
        self.price_change()

    @api.onchange('product_package_mode')
    def _onchange_packaging_mode(self):
        if self.product_id:
            # product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])
            count = self.search_count([('product_id', '=', self.product_id.id),
                                       ('currency_id', '=', self.currency_id.id),
                                       ('product_package_mode', '=', self.product_package_mode.id),
                                       ('state', '=', 'validate')])
            if count > 0:
                price_change_pool = self.env['product.sales.pricelist'].search(
                    [('product_id', '=', self.product_id.id),
                     ('currency_id', '=', self.currency_id.id),
                     ('product_package_mode', '=', self.product_package_mode.id),
                     ('state', '=', 'validate')], order='id desc')[0]
                self.list_price = price_change_pool.new_price
            else:
                self.list_price = 0.00

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.product_id:
            product_pool = self.env['product.product'].search([('id', '=', self.product_id.id)])

            if self.currency_id.name == "BDT":
                count = self.search_count(
                    [('product_id', '=', self.product_id.id), ('currency_id', '=', self.currency_id.id),
                     ('state', '=', 'validate')])
                if count > 0:
                    price_change_pool = self.env['product.sales.pricelist'].search(
                        [('product_id', '=', self.product_id.id),
                         ('currency_id', '=', self.currency_id.id),
                         ('state', '=', 'validate')], order='id desc')[0]
                    self.list_price = price_change_pool.new_price
                else:
                    self.list_price = product_pool.list_price
            else:
                self.list_price = 0.00

    @api.depends('product_id')
    def compute_list_price(self):
        if self.product_id:
            count = self.search_count([('product_id', '=', self.product_id.id),
                                       ('currency_id', '=', self.currency_id.id),
                                       ('state', '=', 'validate')])

            if count > 1:
                price_change_pool = self.env['product.sales.pricelist'].search(
                    [('product_id', '=', self.product_id.id), ('currency_id', '=', self.currency_id.id),
                     ('state', '=', 'validate')], order='id desc')[1]

                if price_change_pool:
                    self.list_price = price_change_pool.new_price
                else:
                    self.list_price = 0.00
            else:
                product_pool = self.env['product.product'].search(
                    [('id', '=', self.product_id.id)])
                self.list_price = product_pool.list_price

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_approve(self):

        self.approver2_id = self.env.user

        # if time.strftime('%Y-%m-%d') > self.effective_date:
        #     raise ValidationError('Effective date must be after final approval date')

        ## Execute below function immedietly to update on Variants History
        # self.env['product.sale.history.line'].pull_automation()

        #self.product_id.write({'discount':self.discount})


        return self.write({'state': 'validate', 'approver2_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def action_validate(self):
        self.approver1_id = self.env.user
        return self.write({'state': 'validate1', 'approver1_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    ### Showing batch
    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        domain = []
        if users_obj.has_group('gbs_application_group.group_cxo'):
            domain = [
                ('state', 'in', ['validate1'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_account'):
            domain = [
                ('state', 'in', ['validate2'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_sale'):
            domain = [
                ('state', 'in', ['confirm'])]
            return domain
        else:
            return False

        return domain


        ## mail notification
        # @api.multi
        # def _notify_approvers(self):
        #     approvers = self.employee_id._get_employee_manager()
        #     if not approvers:
        #         return True
        #     for approver in approvers:
        #         self.sudo(SUPERUSER_ID).add_follower(approver.id)
        #         if approver.sudo(SUPERUSER_ID).user_id:
        #             self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
        #                 [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        #     return True
