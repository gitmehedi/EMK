from odoo import api, fields, models
from datetime import date

class SalePriceChange(models.Model):
    _name = 'sale.price.change'
    _description = "Sale Price Change"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'requested_by'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    product_id = fields.Many2one('product.template', string="Product", required=True, domain=[('sale_ok', '=', True)])
    list_price = fields.Float(string='Old Price', related='product_id.list_price', readonly=True)
    #uom_id = fields.Integer(string='Units of Measure', related='product_id.uom_id')
    new_price = fields.Float(string='New Price', required=True)
    request_date = fields.Datetime(string='Request Date', default=date.today(), readonly=True)
    requested_by = fields.Many2one('hr.employee', string="Requested By", default=_current_employee, readonly=True)
    approver1_id = fields.Many2one('hr.employee', string='First Approval', default=_current_employee, readonly=True)
    approver1_date = fields.Datetime(string='First Approval Date', default=date.today(), readonly=True)
    approver2_id = fields.Many2one('hr.employee', string='Second Approval', default=_current_employee, readonly=True)
    approver2_date = fields.Datetime(string='Second Approval Date', default=date.today(), readonly=True)
    comments = fields.Text(string='Comments')

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft')

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_approve(self):
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


    # manager_id = fields.Many2one('hr.employee', string='First Approval', readonly=True, copy=False,
    #                              help='This area is automatically filled by the user who validate the leave')
    # manager_id2 = fields.Many2one('hr.employee', string='Second Approval', readonly=True, copy=False,
    #                               help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)')


