from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):
        tmpl_dict = defaultdict(lambda: 0.0)
        std_price_update = {}
        for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):
            product_tot_qty_available = move.product_id.qty_available + tmpl_dict[move.product_id.id]
            if move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average':
                lc = self.env['letter.credit'].suspend_security().search(
                    [('name', '=', move.origin), ('region_type', '=', 'foreign')], limit=1)
                if lc:
                    for po in lc.po_ids:
                        if po.invoice_ids:
                            for vb in po.invoice_ids.sorted(lambda r: r.id, reverse=True)[0]:
                                for line in vb.invoice_line_ids.sudo().search([('product_id', '=', move.product_id.id)])[0]:
                                    company_id = move.company_id.id
                                    updated_price_unit =0.0
                                    if vb.currency_id.name == 'BDT':
                                        updated_price_unit = line.price_unit

                                    else:
                                        if vb.conversion_rate:
                                            updated_price_unit = line.price_unit * vb.conversion_rate

                                    amount_unit = std_price_update.get(
                                        (move.company_id.id, move.product_id.id)) or move.product_id.standard_price
                                    new_std_price = ((amount_unit * product_tot_qty_available) + (
                                                updated_price_unit * move.product_qty)) / (
                                                                product_tot_qty_available + move.product_qty)
                                    move.product_id.with_context(force_company=company_id).sudo().write(
                                        {'standard_price': new_std_price})

                                    tmpl_dict[move.product_id.id] += move.product_qty
                                    std_price_update[move.company_id.id, move.product_id.id] = new_std_price

        return
