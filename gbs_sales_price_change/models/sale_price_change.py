from odoo import api, fields, models
from datetime import date
import datetime

class SalePriceChange(models.Model):
    _name = 'sale.price.change'
    _description = "Sale Price Change"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'requested_by'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', required=True)
    list_price = fields.Float(string='Old Price')
    new_price = fields.Float(string='New Price', required=True)
    request_date = fields.Datetime(string='Request Date', default=date.today(), readonly=True)
    requested_by = fields.Many2one('hr.employee', string="Requested By", default=_current_employee, readonly=True)
    approver1_id = fields.Many2one('hr.employee', string='First Approval', default=_current_employee, readonly=True)
    approver1_date = fields.Datetime(string='First Approval Date', default=date.today(), readonly=True)
    approver2_id = fields.Many2one('hr.employee', string='Second Approval', default=_current_employee, readonly=True)
    approver2_date = fields.Datetime(string='Second Approval Date', default=date.today(), readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='State', readonly=True, track_visibility='onchange', copy=False, default='draft')


    @api.onchange('product_id')
    def _onchange_product_form(self):
        product_pool = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
        self.list_price = product_pool.list_price

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

        self.env['product.sale.history.line'].create(vals)

        product_pool = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
        product_pool_update = product_pool.write({'list_price': self.new_price})

        self.state = 'validate'

    @api.multi
    def action_validate(self):
        self.state = 'validate1'

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'

    @api.multi
    def action_draft(self):
        self.state = 'draft'


