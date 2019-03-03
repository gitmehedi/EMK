from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string="Sub Operating Unit",readonly=True)
    segment_id = fields.Many2one('segment', string="Segment",readonly=True)
    acquiring_channel_id = fields.Many2one('acquiring.channel', string="Acquiring Channel",readonly=True)
    servicing_channel_id = fields.Many2one('servicing.channel', string="Servicing Channel",readonly=True)
