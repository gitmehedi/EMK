from odoo import models, fields, api, _


class StockPickingActionLog(models.Model):
    _name = 'stock.picking.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    picking_id = fields.Many2one('stock.picking', string='Picking Reference')
