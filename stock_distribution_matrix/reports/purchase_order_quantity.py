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
        size = 1
        color = 2
        value = list(set([record.product_id.product_tmpl_id.name for record in records.order_quantity_ids]))
        data = {d: {} for d in value}
        size_value = set([val.name for qty in records.order_quantity_ids for val in qty.product_id.attribute_value_ids])

        if records:
            for record in records.order_quantity_ids:
                rec = {
                    'YELLOW': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                    'PIECE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                    'CREAM': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                    'DEEP OLIVE': [(2, 2000), (3, 2000), (4, 2000), (5, 2000)],
                }
                #         rec[]
                #         rec = {
                #             'name': record.product_id.display_name,
                #             'size': record.product_id.default_code,
                #             'quantity': record.quantity,
                #         }
                data[record.product_id.product_tmpl_id.name]['color'].update(rec)

        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('stock_distribution_matrix.purchase_order', docargs)



