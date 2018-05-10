from odoo import api, fields, models, _


class StockIssueReport(models.AbstractModel):
    _name = 'report.stock_issue_report.report_stock_issue'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['category'],
            'total': get_data['total'],
        }
        return self.env['report'].render('stock_issue_report.report_stock_issue', docargs)

    @api.model
    def get_query(self, data):
        date_start = data['date_from']
        date_end = data['date_to']
        operating_unit_id = data['operating_unit_id']
        category_id = data['category_id']
        cat_pool = self.env['product.category']
        cat_lists = []

        if category_id:
            categories = cat_pool.get_categories(category_id)
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'total_qty': 0.0,
                    'total_val': 0.0,
                }
            } for val in cat_pool.search([('id', 'in', categories)])}
        else:
            cat_lists = cat_pool.search([], order='name ASC')
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'total_qty': 0.0,
                    'total_val': 0.0,
                }
            } for val in cat_lists}

        if cat_lists:
            categories = cat_lists.ids

        if len(categories) == 1:
            category_param = "(" + str(data['category_id']) + ")"
        else:
            category_param = str(tuple(categories))

        sql = '''SELECT 		      
                      pt.name AS name,
                      ipl.product_uom_qty AS quantity,
                      pu.name AS unit_name,
                      ipl.product_id,
                      ipl.price_unit AS price,
                      ii.indent_date,
                      pc.name AS category,
                      ipl.price_unit * ipl.product_uom_qty AS total_val
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
				                          ON( pu.id = pt.uom_id )
                    WHERE  ii.operating_unit_id =%s  
                           AND DATE(ii.indent_date) BETWEEN DATE('%s') and DATE('%s')
                           %s
                           
                   ''' % (operating_unit_id, date_start, date_end, category_param)

        return sql
