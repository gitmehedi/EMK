from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class InheritedPickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    lc_id = fields.Many2one('letter.credit', 'LC')

    @api.onchange('lc_id')
    def onchange_lc_id(self):
        for rec in self:
            if rec.lc_id:
                #

                purchase_cost_dist_obj = self.env['purchase.cost.distribution'].sudo().search(
                    [('lc_id', '=', rec.lc_id.id)])
                purchase_cost_distribution_obj = self.env['purchase.cost.distribution'].browse(
                    self.env.context['active_id'])
                if not purchase_cost_distribution_obj.operating_unit_id:
                    raise UserError(
                        "Select Operating Unit First!")

                location_id = self.env['stock.location'].search(
                    [('operating_unit_id', '=', purchase_cost_distribution_obj.operating_unit_id.id), ('name', '=', 'Stock')],
                    limit=1).id
                pickings = self.env['stock.picking'].search(
                    [('origin', '=', rec.lc_id.name), ('state', '=', 'done'),
                     ('location_dest_id', '=', location_id)])

                for picking in pickings:
                    if not picking.mrr_no:
                        raise UserError(
                            "%s - Sound Stock MRR not approved and printed!" % picking.name)

                if purchase_cost_dist_obj:
                    for cost in purchase_cost_dist_obj:
                        if cost.id != purchase_cost_distribution_obj.id:
                            if cost.account_move_id:
                                return
                            else:
                                raise UserError(
                                    "Landed Cost already added for this LC. You need to post journal entry for that Landed Cost First!")

    @api.depends('lc_id')
    def compute_lc_name(self):
        for rec in self:
            if rec.lc_id:
                rec.lc_name = rec.lc_id.name

    lc_name = fields.Char(compute='compute_lc_name')

    @api.depends('pickings')
    def compute_shipment_selected(self):
        for rec in self:
            if rec.pickings:
                rec.shipment_selected = True
            else:
                rec.shipment_selected = False

    shipment_selected = fields.Boolean(compute='compute_shipment_selected')

    @api.depends('supplier')
    def compute_include_purchase_cost(self):
        include_product_purchase_cost = self.env['ir.values'].get_default('account.config.settings',
                                                                          'include_product_purchase_cost')
        for rec in self:
            rec.include_product_purchase_cost = include_product_purchase_cost

    include_product_purchase_cost = fields.Boolean(compute='compute_include_purchase_cost')

    # @api.multi
    # def action_import_picking(self):
    #
    #     purchase_cost_distribution_obj = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
    #     if purchase_cost_distribution_obj:
    #         purchase_cost_distribution_obj.write({'lc_id': self.lc_id.id})
    #     super(InheritedPickingImportWizard, self).action_import_picking()
