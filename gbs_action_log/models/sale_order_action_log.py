from odoo import models, fields, api, _


class SaleOrderActionLog(models.Model):
    _name = 'sale.order.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    order_id = fields.Many2one('sale.order', string='Sale Order Reference')

class ProformaInvoiceActionLog(models.Model):
    _name = 'proforma.invoice.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    pi_id = fields.Many2one('proforma.invoice', string='Sale Order Reference')

class DeliveryAuthorizationActionLog(models.Model):
    _name = 'delivery.authorization.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    delivery_id = fields.Many2one('delivery.authorization', string='Sale Order Reference')