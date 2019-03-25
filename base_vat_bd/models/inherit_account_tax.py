from odoo import models, fields, api, _

class AccountTax(models.Model):
    _name = 'account.tax'
    _order = 'name desc'
    _inherit = ['account.tax','mail.thread']


    name = fields.Char(track_visibility='onchange')
    type_tax_use = fields.Selection(track_visibility='onchange')
    amount_type = fields.Selection(track_visibility='onchange')
    amount = fields.Float(track_visibility='onchange')
    account_id = fields.Many2one(track_visibility='onchange')
    refund_account_id = fields.Many2one(track_visibility='onchange')
    description = fields.Char(track_visibility='onchange')
    tax_group_id = fields.Many2one(track_visibility='onchange')
    analytic = fields.Boolean(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    price_include = fields.Boolean(track_visibility='onchange')
    include_base_amount = fields.Boolean(track_visibility='onchange')
    tax_adjustment = fields.Boolean(track_visibility='onchange')
