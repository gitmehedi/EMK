from odoo import models, fields, api, _


class VendorAdvance(models.Model):
    _name = 'vendor.advance'
    _inherit = ['vendor.advance', 'ir.needaction_mixin']

    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit', required=True,
                                            track_visibility='onchange', readonly=True,
                                            states={'draft': [('readonly', False)]})

    def create_journal(self, journal_id):
        move = super(VendorAdvance, self).create_journal(journal_id)
        if self.sub_operating_unit_id:
            for line in move.line_ids:
                line.write({'sub_operating_unit_id': self.sub_operating_unit_id.id})
        return move