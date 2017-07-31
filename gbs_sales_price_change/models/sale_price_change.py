from odoo import api, fields, models
from datetime import date

class SalePriceChange(models.Model):
    _name = 'sale.price.change'
    _description = "Sale Price Change"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'requested_by'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    #product_id = fields.Many2one('product.template', string="Product", required=True, domain=[('sale_ok', '=', True)], ondelete='cascade')
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', ondelete='cascade')
    list_price = fields.Float(string='Old Price', related='product_id.list_price', readonly=True)
    #uom_id = fields.Integer(string='Units of Measure', related='product_id.uom_id')
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
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft')

    line_ids = fields.One2many('product.sale.history.line','sale_price_history_id')

    @api.multi
    def write(self, values):
        if values.get('new_price'):
            product_pool = self.env['product.product'].search([('product_tmpl_id','=', self.product_id.id)])
            product_pool_update = product_pool.write({'list_price': values.get('new_price')})
            return product_pool_update
        else:
            return super(SalePriceChange, self).write(values)

    # @api.model
    # def create(self, values):
    #     #self.write(values)
    #     super(SalePriceChange, self).create(values)
    #
    #     if values:
    #         product_pool = self.env['product.product'].search([('product_tmpl_id', '=', 2)])
    #         product_pool_update = product_pool.write({'list_price': values.get('new_price')})


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

        self.env['product.sale.history.line'].create(vals)

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


