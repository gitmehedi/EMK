from odoo import fields, models, api


class StockBackorderConfirmationInherit(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.multi
    def process(self):
        res = super(StockBackorderConfirmationInherit, self).process()
        set_challan = self.env['set.challan'].set_challan(self.pick_id.move_lines, self.pick_id.challan_bill_no,
                                                          self.pick_id.challan_date)

        return res

    @api.multi
    def process_cancel_backorder(self):
        res = super(StockBackorderConfirmationInherit, self).process_cancel_backorder()
        set_challan = self.env['set.challan'].set_challan(self.pick_id.move_lines, self.pick_id.challan_bill_no, self.pick_id.challan_date)

        return res

