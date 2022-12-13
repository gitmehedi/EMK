from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):
        tmpl_dict = defaultdict(lambda: 0.0)
        std_price_update = {}
        # Start Custom Logic For GBS : Unit Price will not update for Foreign Purchase (LC & TT). Because landed cost are not added on PO
        include_product_purchase_cost = True
        moves = self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average')
        move_length = len(moves)
        count = 0
        for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):
            product_tot_qty_available = move.product_id.qty_available + tmpl_dict[move.product_id.id]

            # po = self.env['purchase.order'].suspend_security().search([('name', '=', move.origin)], limit=1)
            lc = self.env['letter.credit'].suspend_security().search([('name', '=', move.origin)], limit=1)

            if lc:
                if include_product_purchase_cost:
                    return
                else:
                    for po in lc.po_ids:
                        if po.invoice_ids:
                            invoice_states = po.invoice_ids.mapped('state')
                            if not ('open' in invoice_states or 'paid' in invoice_states):
                                raise UserError("Vendor Bills not found validated or paid.")
                            else:
                                for vb in po.invoice_ids.sorted(lambda r: r.date, reverse=True)[0]:
                                    for line in vb.invoice_line_ids.sudo().search([('product_id', '=', move.product_id.id)])[0]:
                                        company_id = move.company_id.id
                                        updated_price_unit = 0.0
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

                    count = count + 1
                    if count == move_length:
                        return
            # if not po:
            #     # It's mean move coming form production. So need to update Finish goods Unit Price
            #     return super(StockMove, self).product_price_update_before_done()
            #
            # if po.region_type in ('foreign') or po.purchase_by in ('lc','tt'):
            #     return


        super(StockMove, self).product_price_update_before_done()

        # End Custom Logic For GBS