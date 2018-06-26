from odoo import api, models


class PurchasePriceReport(models.AbstractModel):
    _name = 'report.purchase_average_price_report.purchase_price_report_temp'

    @api.multi
    def render_html(self, docids, data=None):
        # get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_id = data['operating_unit_id']
        op_unit_obj = self.env['operating.unit'].search([('id', '=', op_unit_id)])
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)
        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            # 'lines': get_data['product'],
            'address': data['address'],
        }
        return self.env['report'].render('purchase_average_price_report.purchase_price_report_temp', docargs)

    # def get_report_data(self, data):
    #     date_from = data['date_from']
    #     date_start = date_from + ' 00:00:00'
    #     date_to = data['date_to']
    #     date_end = date_to + ' 23:59:59'
    #
    #     sql_avg ='''SELECT sm.product_id,
    #                       pt.name,
    #                       pu.name                 AS uom_name,
    #                       sm.date + interval'6h'  AS move_date
    #                       FROM   stock_move sm
    #                       LEFT JOIN product_product pp
    #                       ON sm.product_id = pp.id
    #                       LEFT JOIN product_template pt
    #                       ON pp.product_tmpl_id = pt.id
    #                       LEFT JOIN product_uom pu
    #                       ON pu.id = pt.uom_id
    #     '''
    #
    #     return {'product': product}