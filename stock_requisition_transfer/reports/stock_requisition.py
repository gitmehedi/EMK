from openerp import models, fields, api


class StockRequisitionTransfer(models.AbstractModel):
    _name = 'report.stock_requisition_transfer.stock_requisition'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_requisition_transfer.stock_requisition')

        records = self.env['stock.requisition.transfer'].search([('id', '=', self.id)])
        data = []

        if records:
            header_info = {}
            header_info['transfer_date'] = records.transfer_date
            header_info['receive_date'] = records.receive_date
            header_info['transfer_user_id'] = records.transfer_user_id.name
            header_info['receive_user_id'] = records.receive_user_id.name
            header_info['my_shop_id'] = records.requested_id.name
            header_info['transfer_shop_id'] = records.to_shop_id.name

        count = 0
        for record in records.product_line_ids:
            rec = {}
            count = count + 1
            rec['sn'] = count
            rec['barcode'] = record.product_id.default_code
            rec['name'] = record.product_id.name
            rec['quantity'] = record.quantity
            rec['receive_quantity'] = record.receive_quantity
            data.append(rec)

        print data

        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'record': header_info,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_requisition_transfer.stock_requisition', docargs)
