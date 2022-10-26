from odoo import fields, models, api


class InheritedPurchaseRFQ(models.Model):
    _inherit = 'purchase.rfq'

    user_remarks = fields.Text()
    manager_remarks = fields.Text()
    procurement_head_remarks = fields.Text()

    order_count_ = fields.Integer(compute='_compute_orders_number_', string='Number of Orders')

    @api.multi
    def _compute_orders_number(self):
        for rfq in self:
            purchase_ids = self.env['purchase.order'].search(
                [('rfq_id', '=', rfq.id),('created_by_cs', '=', False)])
            rfq.order_count = len(purchase_ids)

    @api.multi
    def _compute_orders_number_(self):
        for rfq in self:
            purchase_ids = self.env['purchase.order'].search([('rfq_id', '=', rfq.id), ('state', '!=', 'cancel'), ('created_by_cs', '=', True)])
            rfq.order_count_ = len(purchase_ids)

    state = fields.Selection([
        ('draft', "Draft"),
        ('sent_for_confirmation', "Send for Confirmation"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft', track_visibility='onchange')
