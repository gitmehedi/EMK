from odoo import api, fields, models
from datetime import date


class PurchaseRequisition(models.Model):
    _inherit = ['purchase.requisition']

    department_id = fields.Many2one('hr.department',
                                    string='Department', store=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    buying_type = fields.Selection([('Local', 'Local'), ('Foreign', 'Foreign')], string="Type")

    purchase_by = fields.Selection([('Cash', 'Cash'), ('Credit', 'Credit'), ('LC', 'LC'), ('TT', 'TT')], string="Purchase By")

    requisition_date = fields.Date(string='Requisition Date',default = date.today())

    required_date = fields.Date(string='Required Date')

    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Confirmed'),
                              ('review_plant_incharge', 'Review'),
                              ('approve_head_procurement', 'Waiting For Approval'),('done', 'Approved'),
                              ('cancel', 'Cancelled')],'Status', track_visibility='onchange', required=True,
                             copy=False, default='draft')

    @api.multi
    def action_open(self):
        self.write({'state': 'review_plant_incharge'})

    @api.multi
    def action_reviewed(self):
        self.write({'state': 'approve_head_procurement'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'done'})

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    last_purchse_date = fields.Date(string='Last Purchase Date')
    last_qty = fields.Float(string='Last Purchase Qnty')
    last_product_uom_id = fields.Many2one('product.uom', string='Last Purchase Unit')
    last_price_unit = fields.Float(string='Last Unit Price')
    remark = fields.Char(string='Remarks')
