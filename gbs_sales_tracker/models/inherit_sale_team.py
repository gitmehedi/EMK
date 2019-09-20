from odoo import api, fields, models, tools, _


class SalesTeam(models.Model):
    _inherit = "crm.team"

    name = fields.Char(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    operating_unit_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    use_quotations = fields.Boolean(track_visibility='onchange')
    use_invoices = fields.Boolean(track_visibility='onchange')

class SaleOrderType(models.Model):
    _name = 'sale.order.type'
    _inherit = ['sale.order.type', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    journal_id = fields.Many2one(track_visibility='onchange')
    pricelist_id = fields.Many2one(track_visibility='onchange')
    incoterm_id = fields.Many2one(track_visibility='onchange')
    payment_term_id = fields.Many2one(track_visibility='onchange')
    picking_policy = fields.Selection(track_visibility='onchange')


