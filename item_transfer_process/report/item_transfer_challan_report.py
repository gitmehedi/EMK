from odoo import api, models, _
from odoo.exceptions import ValidationError


class TransferChallanReport(models.AbstractModel):
    _name = 'report.item_transfer_process.report_item_transfer_challan'
    _description = 'Transfer Challan Report'


    @api.multi
    def render_html(self, docids, data=None):

        lending_run_pool = self.env['item.loan.lending']
        docs = lending_run_pool.browse(data.get('active_id'))
        ReportUtility = self.env['report.utility']
        item_lists = []

        data = {}
        data['request_date'] = ReportUtility.getERPDateFormat(ReportUtility.getDateTimeFromStr(docs.request_date))
        data['name'] = docs.name
        data['operating_unit_id'] = docs.operating_unit_id.name
        data['receiving_operating_unit_id'] = docs.receiving_operating_unit_id.name
        data['company_id'] = docs.company_id.name
        data['transfer_date'] = ReportUtility.getERPDateFormat(ReportUtility.getDateTimeFromStr( docs.picking_id.date_done))
        picking_id = docs.picking_id
        move_ids = self.env['stock.move'].search([('picking_id', '=', picking_id.id)])

        for move in move_ids:
            list_obj = {}
            list_obj['product_id']= move.product_id.name
            list_obj['product_qty']= move.product_qty
            list_obj['product_uom'] = move.product_uom.name
            list_obj['product_code'] = move.product_id.code

            item_lists.append(list_obj)

        docargs = {
            'data': data,
            'lists': item_lists
        }

        return self.env['report'].render('item_transfer_process.report_item_transfer_challan', docargs)


