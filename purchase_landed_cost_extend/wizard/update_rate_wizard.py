from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class UpdateWizard(models.TransientModel):
    _name = 'update.rate.wizard'

    @api.model
    def default_get(self, fields):
        res = super(UpdateWizard, self).default_get(fields)
        purchase_cost_distribution_obj = self.env['purchase.cost.distribution'].browse(
            self.env.context['active_id'])
        vb_rate = 0.0
        total_invoice = 0
        for rec in purchase_cost_distribution_obj:
            if rec.lc_id:

                for po in rec.lc_id.po_ids:
                    if po.invoice_ids:
                        invoice_states = po.invoice_ids.mapped('state')
                        if not ('open' in invoice_states or 'paid' in invoice_states):
                            raise UserError("Vendor Bills not found validated or paid!")

                        for vb in po.invoice_ids:
                            if vb.currency_id.name == 'BDT' and po.currency_id.name != 'BDT':
                                vb.conversion_rate = po.currency_id.reverse_rate
                            vb_rate = vb_rate + vb.conversion_rate
                            total_invoice = total_invoice + 1
                    else:
                        raise UserError("Vendor Bills not create for related Purchase Order!")

        if total_invoice == 0:
            raise UserError('Vendor Bill total found zero!')
        res['invoice_avg_currency_rate'] = vb_rate / total_invoice
        res['final_rate'] = vb_rate / total_invoice

        for rec in purchase_cost_distribution_obj:
            if rec.cost_lines:
                rate_in_move = 0
                total_currency_rate = 0
                for move in rec.cost_lines.mapped('move_id'):
                    for po in rec.lc_id.po_ids:
                        if po.invoice_ids:
                            invoice_states = po.invoice_ids.mapped('state')
                            if not ('open' in invoice_states or 'paid' in invoice_states):
                                raise UserError("Vendor Bills not found validated or paid.")
                        for line in po.order_line.filtered(lambda l: l.product_id.id == move.product_id.id):
                            po_price_unit = line.price_unit
                            if po_price_unit > 0 and move.price_unit > 0:
                                rate_in_move = move.price_unit / po_price_unit
                            else:
                                raise UserError("Unit Price for a product found 0!")
                    total_currency_rate = total_currency_rate + rate_in_move
            else:
                raise UserError(_('You need to cost to complete this operation!'))
            res['shipment_rate'] = total_currency_rate / len(rec.cost_lines)
        return res

    invoice_avg_currency_rate = fields.Float('Bill Average Rate',
                                             help='''This value is the average of total Vendor Bill's Rate!''')

    shipment_rate = fields.Float('Shipment Rate')

    @api.constrains('final_rate')
    def _check_final_rate(self):
        if self.final_rate <= 0.0:
            raise ValidationError(_("Rate cannot be negative or zero!"))

    final_rate = fields.Float('Final Rate')

    def update_currency_rate(self):
        purchase_cost_distribution_obj = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])

        if not purchase_cost_distribution_obj.expense_lines:
            raise UserError(_('You need to expense to complete this operation!'))

        include_product_purchase_cost = True

        stock_move_utility = self.env['stock.move.utility']
        if include_product_purchase_cost:
            # stock move can be updated
            if self.final_rate:
                # stock move need to be updated
                for rec in purchase_cost_distribution_obj:
                    for move in rec.cost_lines.mapped('move_id'):
                        po_unit_price = stock_move_utility.get_po_unit_price(move.product_id, purchase_cost_distribution_obj.lc_id)
                        if po_unit_price:
                            stock_move_utility.update_move_price_unit(False, move, 'landed_cost_window', self.final_rate,
                                                                      po_unit_price)

                purchase_cost_distribution_obj.write({'state': 'rate_update', 'currency_rate': self.final_rate})
