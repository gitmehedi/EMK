from odoo import api, fields, models
from datetime import date
import datetime
import time

class SalePriceChange(models.Model):
    _name = 'sale.price.change'
    _description = "Sale Price Change"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'requested_by'
    _order = "approver2_date desc"

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)],
                                 states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)], 'validate': [('readonly', True)]}, string='Product', required=True)
    list_price = fields.Float(string='Old Price')
    new_price = fields.Float(string='New Price', states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate': [('readonly', True)]}, required=True)
    request_date = fields.Datetime(string='Request Date', default=date.today(), readonly=True)
    requested_by = fields.Many2one('hr.employee', string="Requested By", default=_current_employee, readonly=True)

    approver1_id = fields.Many2one('hr.employee', string='First Approval', readonly=True)
    approver2_id = fields.Many2one('hr.employee', string='Second Approval', readonly=True)

    approver1_date = fields.Datetime(string='First Approval Date', readonly=True)
    approver2_date = fields.Datetime(string='Second Approval Date', readonly=True)

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='State', readonly=True, track_visibility='onchange', copy=False, default='draft')

    currency_id = fields.Many2one('res.currency', string="Currency", states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],'validate': [('readonly', True)]}, required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('gbs_sales_price_change'),
                                 required=True)

    @api.onchange('product_id')
    def _onchange_product_form(self):
        product_pool = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
        self.list_price = product_pool.list_price

        if product_pool:
            self.currency_id = product_pool.currency_id.id


    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_approve(self):
        sale_price_obj = self.env['sale.price.change'].browse(self.id)
        vals = {}

        vals['product_id'] = self.product_id.id
        vals['list_price'] = self.list_price
        vals['new_price'] = self.new_price
        vals['sale_price_history_id'] = sale_price_obj.id
        vals['approve_price_date'] = datetime.datetime.now()
        vals['currency_id'] = self.currency_id.id

        self.env['product.sale.history.line'].create(vals)

        product_pool = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
        product_pool_update = product_pool.write({'list_price': self.new_price})

        product_pricelist = self.env['product.pricelist'].search([('currency_id', '=', self.currency_id.id), ('company_id','=', self.company_id.id)])

        pricelist_pool = self.env['product.pricelist.item'].search([('product_tmpl_id', '=', self.product_id.id)])

        if pricelist_pool:
            pricelist_pool.write({'fixed_price':self.new_price, 'pricelist_id': product_pricelist.id})
        else:
            pricelist_pool.create({'fixed_price':self.new_price, 'product_tmpl_id':self.product_id.id, 'pricelist_id': product_pricelist.id})

        return self.write({'approver2_id':self.env.user.employee_ids.id, 'state': 'validate', 'approver2_date': time.strftime('%Y-%m-%d %H:%M:%S')})


    @api.multi
    def action_validate(self):
       # self.approver1_id = self.env.user.employee_ids.id
        return self.write({'approver1_id':self.env.user.employee_ids.id, 'state': 'validate1', 'approver1_date': time.strftime('%Y-%m-%d %H:%M:%S')})


    @api.multi
    def action_refuse(self):
        self.state = 'refuse'

    @api.multi
    def action_draft(self):
        self.state = 'draft'


