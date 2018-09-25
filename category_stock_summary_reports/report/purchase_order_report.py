from datetime import datetime

from openerp import api, models


class PurchaseOrderReport(models.AbstractModel):
    _name = 'report.category_stock_summary_reports.purchase_order_report_qweb'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'category_stock_summary_reports.purchase_order_report_qweb')

        lines = self.get_report_data(data)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'record': data,
            'lines': lines,
        }
        return report_obj.render('category_stock_summary_reports.purchase_order_report_qweb', docargs)

    def get_report_data(self, data):
        date_start = data['date_from']
        date_end = data['date_to']

        sql = '''
                SELECT po.id AS id,
                        po.name AS po_name,
                        pt.name AS product_name,
                        pu.name AS uom_name,
                        po.state AS state,
                        pol.price_unit AS price,
                        po.date_order AS date,
                        pol.product_qty AS order_qty,
                        (pol.product_qty * pol.price_unit) AS order_value,
                        pol.receive_qty AS receive_qty,
                        (pol.receive_qty * pol.price_unit) AS receive_value,
                        (pol.product_qty-pol.receive_qty) AS remain_qty,
                        (pol.product_qty-pol.receive_qty)*pol.price_unit AS remain_value
                FROM purchase_order po
                    LEFT JOIN purchase_order_line pol
                        ON (po.id = pol.order_id)
                    LEFT JOIN product_template pt 
                        ON pol.product_id = pt.id 
                    LEFT JOIN product_uom pu 
                        ON(pu.id = pt.uom_id ) 
                WHERE date_order BETWEEN '%s' AND '%s'
                        AND po.state in ('approved','confirmed','done')
                        AND pol.product_qty > pol.receive_qty
                ORDER BY po.id ASC
              ''' % (date_start, date_end)

        values = {}
        self.env.cr.execute(sql)
        for vals in self.env.cr.dictfetchall():
            if vals:
                po_name = str(vals['po_name'])
                if po_name in values:
                    values[po_name]['values'].append(vals)

                else:
                    values[po_name] = {'values': [],
                                       'order_qty': 0,
                                       'order_value': 0,
                                       'receive_qty': 0,
                                       'receive_value': 0,
                                       'remain_qty': 0,
                                       'remain_value': 0,
                                       'state': vals['state']
                                       }
                    values[po_name]['values'].append(vals)

                values[po_name]['order_qty'] = values[po_name]['order_qty'] + vals['order_qty']
                values[po_name]['order_value'] = values[po_name]['order_value'] + vals['order_value']
                values[po_name]['receive_qty'] = values[po_name]['receive_qty'] + vals['receive_qty']
                values[po_name]['receive_value'] = values[po_name]['receive_value'] + vals['receive_value']
                values[po_name]['remain_qty'] = values[po_name]['remain_qty'] + vals['remain_qty']
                values[po_name]['remain_value'] = values[po_name]['remain_value'] + vals['remain_value']
                

        return values
