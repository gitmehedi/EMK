from odoo import api, fields, models, _


class StockIssueReport(models.AbstractModel):
    _name = 'report.stock_issue_report.report_stock_issue'

    @api.multi
    def render_html(self, docids, data=None):
        lists = []
        sql = self.get_query(data)

        self._cr.execute(sql)
        for record in self._cr.fetchall():
           lists.append(record)

        docargs = {
            'data': data,
            'lists': lists,
        }
        return self.env['report'].render('stock_issue_report.report_stock_issue', docargs)

    @api.model
    def get_query(self, data):
        _where = ' AND department_id=' + str(data['department_id']) if data['department_id'] else ''

        sql = '''SELECT
                      pt.name,
                      ipl.product_uom_qty,
                      pu.name AS puom_name,
                      ipl.qty_available,
                      dpt.name AS dpt_name,
                      ipl.product_uom,
                      ipl.product_id,
                      ii.indent_date,
                      pu.name AS puom_name,
                      ii.department_id,
                      ii.operating_unit_id,
                      ou.name AS opu_name
                    FROM indent_indent AS ii
                    LEFT JOIN indent_product_lines AS ipl
                      ON ii.id = ipl.indent_id
                    LEFT JOIN operating_unit ou
                      ON (ou.id = ii.operating_unit_id)
                    LEFT JOIN hr_department AS dpt
                      ON (dpt.id = ii.department_id)
                    LEFT JOIN product_product AS pp
                      ON (pp.id = ipl.product_id)
                    LEFT JOIN product_uom AS pu
                      ON (pu.id = ipl.product_uom)
                    LEFT JOIN product_template pt
                      ON (pp.product_tmpl_id = pt.id)
                    WHERE  ii.operating_unit_id =%s  
                           AND DATE(ii.indent_date) BETWEEN DATE('%s') and DATE('%s')
                           %s
                           
                   ''' % (data['operating_unit_id'], data['from_date'], data['to_date'], _where)

        return sql
