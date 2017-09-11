from openerp import models, fields, api


class StockRequisitionTransfer(models.AbstractModel):
    _name = 'report.stock_distribution_matrix.purchase_order'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_distribution_matrix.purchase_order')
        records = self.env['purchase.order'].search([('id', '=', self.id)])
        # data = {
        #     "256L": {
        #         'size': ['S', 'M', 'L', 'Multi'],
        #         'color': {
        #             'YELLOW': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #             'PIECE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #             'CREAM': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #             'DEEP OLIVE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #         }
        #     },
        #     "8000": {
        #         'size': ['S', 'M', 'L', 'XL'],
        #         'color': {
        #             'YELLOW': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #             'PIECE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #             'CREAM': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #             'DEEP OLIVE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
        #         }
        #     }
        # }
        color = 1
        size = 2
        # records.order_quantity_ids[4].product_id.attribute_value_ids[1].attribute_id
        value = list(set([record.product_id.product_tmpl_id.name for record in records.order_quantity_ids]))

        colors = set([val.name for qty in records.order_quantity_ids for val in qty.product_id.attribute_value_ids if
                      val.attribute_id.id == color])
        sizes = set([val.name for qty in records.order_quantity_ids for val in qty.product_id.attribute_value_ids if
                     val.attribute_id.id == size])
        data = {d: {'color': {c:[] for c in colors}} for d in value}
        if records:
            for record in records.order_quantity_ids:
                for clr in record.product_id.attribute_value_ids:
                    if clr.name in colors:
                        data[record.product_id.product_tmpl_id.name]['color'][clr.name].append((record.product_id.default_code, record.quantity))
                # rec = {
                #     'YELLOW': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                #     'PIECE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                #     'CREAM': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                #     'DEEP OLIVE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                # }
                #         rec[]
                #         rec = {
                #             'name': record.product_id.display_name,
                #             'size': record.product_id.default_code,
                #             'quantity': record.quantity,
                #         }


        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_distribution_matrix.purchase_order', docargs)
