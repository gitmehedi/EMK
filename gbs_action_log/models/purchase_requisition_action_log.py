from odoo import models, fields, api, _


class PurchaseRequisitionActionLog(models.Model):
    _name = 'purchase.requisition.action.log'

    action_id = fields.Many2one('users.action', string='Action Performed')
    performer_id = fields.Many2one('res.users', string='Approve User')
    perform_date = fields.Datetime(string='Action Performed Date')
    requisition_id = fields.Many2one('purchase.requisition', string='Requisition Reference')
