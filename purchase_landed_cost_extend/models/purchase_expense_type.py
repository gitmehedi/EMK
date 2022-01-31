from odoo import models, fields, api, _


class PurchaseExpenseType(models.Model):
    _name = 'purchase.expense.type'
    _inherit = ['purchase.expense.type', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    default_expense = fields.Boolean(track_visibility='onchange')
    calculation_method = fields.Selection(track_visibility='onchange')
    default_amount = fields.Float(track_visibility='onchange')
