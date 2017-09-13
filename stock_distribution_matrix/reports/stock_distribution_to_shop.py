from openerp import models, fields, api


class StockRequisitionTransfer(models.AbstractModel):
    _name = 'report.stock_distribution_matrix.stock_distribution_to_shop'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_distribution_matrix.stock_distribution_to_shop')

        records = self.env['stock.distribution.to.shop'].search([('id', '=', self.id)])
        data, count = [], 0

        if records:
            header = {}
            header['product_name'] = records.product_tmp_id.name
            header['warehouse'] = records.warehoue_id.name

        for record in records.stock_distribution_lines_ids:
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
