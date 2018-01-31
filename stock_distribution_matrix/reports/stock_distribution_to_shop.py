from openerp import models, fields, api


class StockRequisitionTransfer(models.AbstractModel):
    _name = 'report.stock_distribution_matrix.stock_distribution_to_shop'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_distribution_matrix.stock_distribution_to_shop')

        records = self.env['stock.distribution.to.shop'].search([('id', '=', self.id)])
        data, count = {}, 0

        configObj = self.env['pos.config'].search([('state', '=', 'active'), ('active_shop', '=', True)])
        config = {conf.id: conf.name for conf in configObj}

        for val in records.product_tmp_id.product_variant_ids:
            data[val.id] = {
                'name': val.display_name,
                'value': {key: {'name': val, 'value': None} for key, val in config.iteritems()}
            }

        if records:
            header = {}
            header['product_name'] = records.product_tmp_id.name
            header['warehouse'] = records.warehoue_id.name
            header['name'] = records.name
        #
        for record in records.stock_distribution_lines_ids:
            data[record.product_id.id]['value'][record.pos_shop_id.id]['value'] = int(record.distribute_qty)

        docargs = {
            'doc_ids': self._ids,
            'data': data,
            'record': header,
            'config': config,
            'doc_model': report.model,
            'docs': self,

        }

        return report_obj.render('stock_distribution_matrix.stock_distribution_to_shop', docargs)
