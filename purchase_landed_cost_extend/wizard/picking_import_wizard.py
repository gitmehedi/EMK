from odoo import models, fields, api


class PickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    def _get_default_operating_unit_id(self):
        if self.env.context.get('active_id'):
            distribution = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
            return distribution.operating_unit_id.id

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=_get_default_operating_unit_id)

    @api.depends('lc_id')
    def _journal_entry_created(self):
        for rec in self:
            if rec.lc_id:
                rec.journal_entry_created = True
                purchase_cost_dist_obj = self.env['purchase.cost.distribution'].sudo().search(
                    [('lc_id', '=', rec.lc_id.id)])
                if purchase_cost_dist_obj:
                    for cost_dist in purchase_cost_dist_obj:
                        if cost_dist.account_move_id:
                            rec.journal_entry_created = True
                        else:
                            rec.journal_entry_created = False

    journal_entry_created = fields.Boolean(compute='_journal_entry_created')
