from openerp import models, fields, api


class StockRequisitionTransfer(models.AbstractModel):
    _name = 'report.stock_distribution_matrix.purchase_order'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_distribution_matrix.purchase_order')
        records = self.env['purchase.order'].search([('id', '=', self.id)])

        color, size = 1, 2

        value = list(set([record.product_id.product_tmpl_id.name for record in records.order_quantity_ids]))
        colors = set([val.name for qty in records.order_quantity_ids for val in qty.product_id.attribute_value_ids if
                      val.attribute_id.id == color])
        sizes = set([val.name for qty in records.order_quantity_ids for val in qty.product_id.attribute_value_ids if
                     val.attribute_id.id == size])

        data = {d: {'color': {c: {s: {} for s in sizes} for c in colors}} for d in value}

        if records:
            for record in records.order_quantity_ids:
                sz = None
                cl = None
                for clr in record.product_id.attribute_value_ids:
                    if clr.name in sizes:
                        sz = clr.name
                    if clr.name in colors:
                        cl = clr.name

                    if sz and cl:
                        data[record.product_id.product_tmpl_id.name]['color'][cl][sz][
                            'code'] = record.product_id.default_code
                        data[record.product_id.product_tmpl_id.name]['color'][cl][sz]['qty'] = record.quantity

        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'sizes': sizes,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_distribution_matrix.purchase_order', docargs)
