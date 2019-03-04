from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string="Sub Branch")
    segment_id = fields.Many2one('segment', string="Segment")
    acquiring_channel_id = fields.Many2one('acquiring.channel', string="AC")
    servicing_channel_id = fields.Many2one('servicing.channel', string="SC")
    operating_unit_id  = fields.Many2one(string='Branch')
