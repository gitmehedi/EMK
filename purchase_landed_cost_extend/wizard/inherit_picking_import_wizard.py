from odoo import fields, models, api


class InheritedPickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    lc_id = fields.Many2one('letter.credit', 'LC')

    @api.multi
    def action_import_picking(self):
        purchase_cost_distribution_obj = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
        if purchase_cost_distribution_obj:
            purchase_cost_distribution_obj.write({'lc_id': self.lc_id.id})
        super(InheritedPickingImportWizard, self).action_import_picking()

