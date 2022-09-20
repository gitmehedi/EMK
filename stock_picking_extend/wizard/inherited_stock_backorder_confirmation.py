from odoo import fields, models, api


class StockBackorderConfirmationInherit(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.multi
    def process(self):
        # checking if current picking id is input location
        operating_unit = self.pick_id.location_dest_id.operating_unit_id
        input_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit.id), ('name', '=', 'Input')],
            limit=1).id
        qc_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit.id), ('name', '=', 'Quality Control')],
            limit=1).id
        sound_stock_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit.id), ('name', '=', 'Stock')],
            limit=1).id
        # input -> qc
        if self.pick_id.location_dest_id.id == input_location_id:
            # checking next picking is qc
            qc_pick_id = self.env['stock.picking'].browse(self.pick_id.id + 1)
            if qc_pick_id and qc_pick_id.location_dest_id.id == qc_location_id and qc_pick_id.origin == self.pick_id.origin:
                qc_pick_id.write(
                    {'challan_bill_no': self.pick_id.challan_bill_no, 'challan_date': self.pick_id.challan_date})

        # qc -> sound stock
        if self.pick_id.location_dest_id.id == qc_location_id:
            # checking next picking is sound stock
            sound_stock_pick = self.env['stock.picking'].browse(self.pick_id.id + 1)
            if sound_stock_pick and sound_stock_pick.location_dest_id.id == sound_stock_location_id and sound_stock_pick.origin == self.pick_id.origin:
                sound_stock_pick.write(
                    {'challan_bill_no': self.pick_id.challan_bill_no, 'challan_date': self.pick_id.challan_date})

        return super(StockBackorderConfirmationInherit, self).process()

    @api.multi
    def process_cancel_backorder(self):
        # checking if current picking id is input location
        operating_unit = self.pick_id.location_dest_id.operating_unit_id
        input_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit.id), ('name', '=', 'Input')],
            limit=1).id
        qc_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit.id), ('name', '=', 'Quality Control')],
            limit=1).id
        sound_stock_location_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', operating_unit.id), ('name', '=', 'Stock')],
            limit=1).id
        # input -> qc
        if self.pick_id.location_dest_id.id == input_location_id:
            # checking next picking is qc
            qc_pick_id = self.env['stock.picking'].browse(self.pick_id.id + 1)
            if qc_pick_id and qc_pick_id.location_dest_id.id == qc_location_id and qc_pick_id.origin == self.pick_id.origin:
                qc_pick_id.write(
                    {'challan_bill_no': self.pick_id.challan_bill_no, 'challan_date': self.pick_id.challan_date})

        # qc -> sound stock
        if self.pick_id.location_dest_id.id == qc_location_id:
            # checking next picking is sound stock
            sound_stock_pick = self.env['stock.picking'].browse(self.pick_id.id + 1)
            if sound_stock_pick and sound_stock_pick.location_dest_id.id == sound_stock_location_id and sound_stock_pick.origin == self.pick_id.origin:
                sound_stock_pick.write(
                    {'challan_bill_no': self.pick_id.challan_bill_no, 'challan_date': self.pick_id.challan_date})

        return super(StockBackorderConfirmationInherit, self).process_cancel_backorder()
