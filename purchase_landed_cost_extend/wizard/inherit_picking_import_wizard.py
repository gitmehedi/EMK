from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class InheritedPickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    lc_id = fields.Many2one('letter.credit', 'LC')

    @api.onchange('lc_id')
    def onchange_lc_id(self):
        for rec in self:
            if rec.lc_id:
                purchase_cost_dist_obj =self.env['purchase.cost.distribution'].sudo().search([('lc_id','=',rec.lc_id.id)])
                if purchase_cost_dist_obj:
                    for cost in purchase_cost_dist_obj:
                        if cost.account_move_id:
                            return
                        else:
                            raise UserError(
                                "Landed Cost already added for this LC. You need to post journal entry for that Landed Cost First!")

    ################based on flag TRUE######################

    @api.onchange('pickings', 'lc_id')
    def onchange_pickings(self):
        for rec in self:
            if rec.pickings and rec.lc_id:
                total_currency_rate = 0
                for picking in rec.pickings:
                    rate_in_move = 0
                    for move in picking.move_lines:
                        # compare with po line product unit price
                        for po in rec.lc_id.po_ids:
                            if po.invoice_ids:
                                invoice_states = po.invoice_ids.mapped('state')
                                if not ('open' in invoice_states or 'paid' in invoice_states):
                                    raise UserError("Vendor Bills not found validated or paid.")
                            for line in po.order_line.filtered(lambda l: l.product_id.id == move.product_id.id):
                                po_price_unit = line.price_unit
                                if po_price_unit > 0 and move.price_unit > 0:
                                    rate_in_move = move.price_unit / po_price_unit
                                   # rec.currency_rate = rate_in_move
                                   # rec.hidden_currency_rate = rate_in_move
                                else:
                                    raise UserError("Unit Price for a product found 0!")
                    total_currency_rate = total_currency_rate + rate_in_move

                rec.currency_rate = total_currency_rate / len(rec.pickings)
                rec.hidden_currency_rate = total_currency_rate / len(rec.pickings)
    currency_rate = fields.Float('Currency Rate')
    hidden_currency_rate = fields.Float('Hidden Currency Rate')

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

    @api.multi
    def action_import_picking(self):
        include_product_purchase_cost = self.env['ir.values'].get_default('account.config.settings',
                                                                          'include_product_purchase_cost')

        stock_move_utility = self.env['stock.move.utility']
        if include_product_purchase_cost:
            # stock move can be updated
            if self.currency_rate != self.hidden_currency_rate and self.currency_rate > 0:
                # stock move need to be updated
                for rec in self:
                    for picking in rec.pickings:
                        for move in picking.move_lines:
                            stock_move_utility.update_move_price_unit(rec.lc_id.po_ids,move,'landed_cost_window',self.currency_rate)


        purchase_cost_distribution_obj = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
        if purchase_cost_distribution_obj:
            purchase_cost_distribution_obj.write({'lc_id': self.lc_id.id,'currency_rate':self.currency_rate})
        super(InheritedPickingImportWizard, self).action_import_picking()
