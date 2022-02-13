from odoo import models, fields, api
from odoo.tools import frozendict


class PickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    def _get_default_operating_unit_id(self):
        if self.env.context.get('active_id'):
            distribution = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
            return distribution.operating_unit_id.id

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=_get_default_operating_unit_id)
