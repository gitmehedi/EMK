from odoo import fields, models, api


class InheritStockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    @api.multi
    def process(self):
        res = super(InheritStockImmediateTransfer, self).process()
        set_challan = self.env['set.challan'].set_challan(self.pick_id.move_lines, self.pick_id.challan_bill_no,
                                                          self.pick_id.challan_date)

        return res
