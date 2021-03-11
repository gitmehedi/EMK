from odoo import models, fields, api, _


class PurchaseOrderActionLog(models.Model):
    _name = 'purchase.order.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    order_id = fields.Many2one('purchase.order', string='Purchase Order Reference')
