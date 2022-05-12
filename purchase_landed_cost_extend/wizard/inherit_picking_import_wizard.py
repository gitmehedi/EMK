from odoo import fields, models, api


class InheritedPickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    lc_id = fields.Many2one('letter.credit', 'LC')