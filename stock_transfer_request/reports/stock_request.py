from openerp import models, fields, api


class StockTransferRequestReport(models.AbstractModel):
    _name = 'report.stock_transfer_request.stock_request'

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
        report = report_obj._get_report_from_name('stock_transfer_request.stock_request')

        records = self.env['stock.transfer.request'].search([('id', '=', self.id)])
        data = []

        if records:
            header_info = {}
            header_info['name'] = records.name
            header_info['transfer_date'] = records.transfer_date
            header_info['receive_date'] = records.receive_date
            header_info['transfer_user_id'] = records.transfer_user_id.name
            header_info['receive_user_id'] = records.receive_user_id.name
            header_info['my_shop_id'] = records.my_shop_id.name
            header_info['transfer_shop_id'] = records.transfer_shop_id.name

        count = 0
        total = {}
        total['transfer'] = 0
        total['receive'] = 0

        for record in records.product_line_ids:
            rec = {}
            count = count + 1
            rec['sn'] = count
            rec['barcode'] = record.product_id.default_code
            rec['name'] = self.format_product(record.product_id)
            rec['uom'] = record.product_id.uom_id.name
            rec['quantity'] = record.quantity
            receive = record.receive_quantity if record.receive_quantity else None
            rec['receive_quantity'] = receive
            total['transfer'] = total['transfer'] + record.quantity
            if receive > 0:
                total['receive'] = total['receive'] + receive
            data.append(rec)

        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'total': total,
            'record': header_info,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_transfer_request.stock_request', docargs)
