from datetime import datetime

from openerp import api, models


class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.product_requisition.report_all_branch_requisition_report_view_qweb'

    @api.model
    def get_data(self, data, branch):
        lines = {}
        self.env.cr.execute("""
                    SELECT
                        pr.operating_unit_id,
                        ou.name AS ou_name, 
                        prl.product_id,
                        pp.name_template AS p_name,
                        prl.product_required_qty
                    FROM product_requisition pr
                    INNER JOIN product_requisition_line prl
                        ON(prl.requisition_id=pr.id)
                    LEFT JOIN operating_unit ou
                        ON(pr.operating_unit_id = ou.id )
                    LEFT JOIN product_product pp
                        ON(prl.product_id = pp.id )
                    WHERE pr.period_id= %s AND pr.state='submit'
                    ORDER BY pr.operating_unit_id ASC, prl.product_id ASC
                    """, (data['period_id'],))

        for record in self.env.cr.dictfetchall():
            name = self.env['product.product'].search([('id','=',record['product_id'])],limit=1).display_name
            if name not in lines:
                lines[name] = {}
                lines[name]['period'] = {val.operating_unit_id.name: 0 for val in branch}
                lines[name]['value'] = 0
                lines[name]['no_of_value'] = 0
                lines[name]['average'] = 0
            lines[name]['period'][record['ou_name']] = record['product_required_qty']
            lines[name]['value'] = lines[name]['value'] + record['product_required_qty']
            if record['product_required_qty']:
                lines[name]['no_of_value'] = lines[name]['no_of_value'] + 1
                lines[name]['average'] = round(lines[name]['value'] / lines[name]['no_of_value'], 2)

        return lines

    @api.multi
    def render_html(self, data=None):
        header = {}
        branch = self.env['product.requisition'].search(
            [('period_id', '=', data['period_id']), ('state', '=', 'submit')], order='operating_unit_id ASC')

        header[0] = 'SL'
        header[1] = 'Product'
        for pr in branch:
            header[len(header)] = pr.operating_unit_id.name
        header[len(header)] = 'Total'
        header[len(header)] = 'Average'

        requisition = self.get_data(data, branch)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'header': header,
            'lines': requisition
        }
        return self.env['report'].render('product_requisition.report_all_branch_requisition_report_view_qweb', docargs)
