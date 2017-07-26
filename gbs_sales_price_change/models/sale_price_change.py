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
    new_price = fields.Float(string='New Price')
    request_date = fields.Datetime(string='Request Date', default=date.today(), readonly=True)
    requested_by = fields.Many2one('hr.employee', string="Requested By", default=_current_employee, readonly=True)
    approver1_id = fields.Many2one('res.user', string='First Approval', readonly=True)
    approver1_date = fields.Datetime(string='First Approval Date', default=date.today(), readonly=True)
    approver2_id = fields.Many2one('res.user', string='Final Approval', readonly=True)
    approver2_date = fields.Datetime(string='Final Approval Date', default=date.today(), readonly=True)
    comments = fields.Text(string='Comments')

    # manager_id = fields.Many2one('hr.employee', string='First Approval', readonly=True, copy=False,
    #                              help='This area is automatically filled by the user who validate the leave')
    # manager_id2 = fields.Many2one('hr.employee', string='Second Approval', readonly=True, copy=False,
    #                               help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)')


