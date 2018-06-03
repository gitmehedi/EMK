from odoo import api, fields, models, _


class StockIssueReport(models.AbstractModel):
    _name = 'report.stock_issue_report.report_stock_issue'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_id = data['operating_unit_id']
        op_unit_obj = self.env['operating.unit'].search([('id', '=', op_unit_id)])
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'product_lines': get_data['product'],
            'total': get_data['total'],
            'address': data['address'],
        }
        return self.env['report'].render('stock_issue_report.report_stock_issue', docargs)


    def get_report_data(self, data):
        date_start = data['from_date']
        date_end = data['to_date']
        operating_unit_id = data['operating_unit_id']
        product = []
        grand_total = {
            'title': 'GRAND TOTAL',
            'total_out_val': 0,
        }

        sql = '''SELECT 		      
                      pt.name             AS pt_name,
                      ipl.product_uom_qty AS quantity,
                      ipl.received_qty    AS receive_quantity,
                      pu.name             AS unit_name,
                      ipl.product_id,
                      ipl.price_unit      AS price,
                      ii.indent_date,
                      COALESCE((ipl.price_unit * ipl.received_qty),0) AS total_val
                  FROM indent_indent AS ii
                  LEFT JOIN indent_product_lines AS ipl
                      ON ii.id = ipl.indent_id
                  LEFT JOIN product_product pp
                      ON ipl.product_id = pp.id
                  LEFT JOIN product_template pt
                      ON pp.product_tmpl_id = pt.id             
                  LEFT JOIN product_uom pu
				      ON( pu.id = pt.uom_id )
                  WHERE  ii.operating_unit_id = '%s'
                  AND Date_trunc('day', ii.indent_date) BETWEEN DATE '%s' and DATE '%s'
                           
                   ''' % (operating_unit_id, date_start, date_end)

        self.env.cr.execute(sql)
        for vals in self.env.cr.dictfetchall():
            if vals:
                product.append(vals)

                grand_total['total_out_val'] = grand_total['total_out_val'] + vals['total_val']

        return {'product': product, 'total': grand_total}