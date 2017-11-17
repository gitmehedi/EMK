from openerp import models, fields, api


class ChallanReport(models.AbstractModel):
    _name = 'report.stock_distribution_matrix.challan_report'

    def format_product(self, product_name):
        attr = product_name.attribute_value_ids
        name = ''
        if attr:
            name = "{0}({1},{2})".format(product_name.name, attr[0].name, attr[1].name)
        else:
            name =  product_name.name

        if product_name.product_tmpl_id.product_brand_id:
            return "{0}({1})".format(name,product_name.product_tmpl_id.product_brand_id.name)

        return name

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
        total = {}
        total['transfer'] = 0
        total['receive'] = 0
        for record in records.stock_distribution_lines_ids:
            rec = {}
            count = count + 1
            rec['sn'] = count
            rec['barcode'] = record.product_id.default_code
            rec['name'] = self.format_product(record.product_id)
            rec['uom'] = record.product_uom_id.name
            rec['transfer_qty'] = record.transfer_qty
            receive = record.receive_qty if record.receive_qty else None
            rec['receive_qty'] = receive
            data.append(rec)

            total['transfer'] = total['transfer'] + record.transfer_qty
            if receive > 0:
                total['receive'] = total['receive'] + receive


        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'total': total,
            'record': header_info,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_distribution_matrix.challan_report', docargs)
