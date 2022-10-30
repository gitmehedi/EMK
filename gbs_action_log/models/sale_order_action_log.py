from odoo import models, fields, api, _


class SaleOrderActionLog(models.Model):
    _name = 'sale.order.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    order_id = fields.Many2one('sale.order', string='Sale Order Reference')
