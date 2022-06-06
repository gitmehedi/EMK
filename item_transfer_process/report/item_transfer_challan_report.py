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
        employee_information = self.env['employee.information.from.user'].get_employee_information(
        docs.issuer_id.id)
        employee_name = (employee_information[0])
        item_lists = []

        data = {}
        data['name'] = docs.name
        data['operating_unit_id'] = docs.operating_unit_id.name
        data['receiving_operating_unit_id'] = docs.receiving_operating_unit_id.name
        data['company_id'] = docs.company_id.name
        data['employee_name'] = employee_name
        picking_id = docs.picking_id
        move_ids = self.env['stock.move'].search([('picking_id', '=', picking_id.id)])

        for move in move_ids:
            data['transfer_date'] = ReportUtility.getERPDateFormat(ReportUtility.getDateTimeFromStr(move.date))
            list_obj = {}
            if move.product_id:
                pro_name = move.product_id.name_get()[0][1]
                list_obj['product_id']= pro_name
                list_obj['product_qty']= move.product_qty
                list_obj['product_uom'] = move.product_uom.name
                list_obj['product_code'] = move.product_id.code

            item_lists.append(list_obj)

        docargs = {
            'data': data,
            'lists': item_lists
        }

        return self.env['report'].render('item_transfer_process.report_item_transfer_challan', docargs)


