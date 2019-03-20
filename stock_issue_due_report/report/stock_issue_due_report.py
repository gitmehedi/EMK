from odoo import api, fields, models, _


class StockIssueDueReport(models.AbstractModel):
    _name = 'report.stock_issue_due_report.report_stock_issue_due'

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
            'product_lines': get_data['category'],
            'total': get_data['total'],
            'address': data['address'],
        }
        return self.env['report'].render('stock_issue_due_report.report_stock_issue_due', docargs)


    def get_report_data(self, data):
        date_from = data['from_date']
        date_start = date_from + ' 00:00:00'
        date_to = data['to_date']
        date_end = date_to + ' 23:59:59'
        stock_location_id = data['stock_location_id']
        cat_pool = self.env['product.category']
        category = {val.name: {
            'product': [],
            'sub-total': {
                'title': 'SUB TOTAL',
                'total_issue_qty': 0.0,
                'total_due_qty': 0.0,
            }
        } for val in cat_pool.search([])}

        grand_total = {
            'title': 'GRAND TOTAL',
            'total_issue_qty': 0,
            'total_due_qty': 0,
        }

        sql = '''SELECT ipl.product_id,
                        pc.name             AS category,
                        pt.name             AS pt_name,
                        pp.default_code     AS code,
                        pu.name             AS uom_name,
                        (SELECT array_to_string(array_agg(pv.name), ',')
                            FROM product_attribute_value_product_product_rel pr
		                    LEFT JOIN product_attribute_value pv
			                    ON pv.id = pr.product_attribute_value_id
                            WHERE pr.product_product_id = ipl.product_id
                            GROUP BY pr.product_product_id)  AS variant_name,
                        sum(ipl.product_uom_qty) AS quantity,
                        sum(COALESCE((ipl.product_uom_qty),0) - COALESCE((ipl.received_qty), 0)) AS due_qty
                 FROM indent_indent AS ii
                 LEFT JOIN indent_product_lines AS ipl
                      ON ii.id = ipl.indent_id
                 LEFT JOIN product_product pp
                      ON ipl.product_id = pp.id
                 LEFT JOIN product_template pt
                      ON pp.product_tmpl_id = pt.id
				 LEFT JOIN product_category pc
                      ON pt.categ_id = pc.id
                 LEFT JOIN product_uom pu 
                      ON pu.id = pt.uom_id
                 WHERE
                    (COALESCE((ipl.product_uom_qty),0) - COALESCE((ipl.received_qty), 0)) > 0
                 AND
                    ii.stock_location_id ='%s'
                 AND
                    Date_trunc('day', ii.indent_date + interval'6h') BETWEEN DATE '%s' and DATE '%s'
                 GROUP BY category,ipl.product_id,pt_name,pu.name,pp.default_code,variant_name
                  ''' % (stock_location_id, date_start, date_end)

        self.env.cr.execute(sql)
        for vals in self.env.cr.dictfetchall():
            if vals:
                category[vals['category']]['product'].append(vals)
                total = category[vals['category']]['sub-total']
                total['name'] = vals['category']
                total['total_issue_qty'] = total['total_issue_qty'] + vals['quantity']
                total['total_due_qty'] = total['total_due_qty'] + vals['due_qty']
                grand_total['total_issue_qty'] = grand_total['total_issue_qty'] + vals['quantity']
                grand_total['total_due_qty'] = grand_total['total_due_qty'] + vals['due_qty']

        return {'category': category, 'total': grand_total}