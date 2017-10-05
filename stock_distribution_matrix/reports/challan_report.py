from openerp import models, fields, api


class ChallanReport(models.AbstractModel):
    _name = 'report.stock_distribution_matrix.challan_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_distribution_matrix.challan_report')

        records = self.env['warehouse.to.shop.distribution'].search([('id', '=', self.id)])
        data = []

        if records:
            header_info = {}
            header_info['chalan_no'] = records.name
            header_info['distribute_date'] = records.distribute_date
            header_info['receive_date'] = records.receive_date
            header_info['warehoue_id'] = records.warehoue_id.name
            header_info['shop_id'] = records.shop_id.name

        count = 0
        for record in records.stock_distribution_lines_ids:
            rec = {}
            count = count + 1
            rec['sn'] = count
            rec['barcode'] = record.product_id.default_code
            rec['name'] = record.product_id.name
            rec['transfer_qty'] = record.transfer_qty
            rec['receive_qty'] = record.receive_qty if record.receive_qty else None
            data.append(rec)

        print data

        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'record': header_info,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_distribution_matrix.challan_report', docargs)
