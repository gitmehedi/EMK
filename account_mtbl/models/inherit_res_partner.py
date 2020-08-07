from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_sou_id = fields.Many2one('sub.operating.unit', string='Sequence', copy=False,
                                                      track_visibility='onchange', required=True)

    @api.onchange('property_account_payable_id')
    def _onchange_property_account_payable_id(self):
        for rec in self:
            rec.property_account_payable_sou_id = None
