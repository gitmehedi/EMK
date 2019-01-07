from odoo import api,models,fields
from odoo.tools.misc import formatLang

class PurchaseReport(models.AbstractModel):
    _name = "report.purchase_reports.report_pending_purchase"

    sql_str = """SELECT pr_line.id, pr_line.requisition_id, pr.name, pt.name,
                        pr_line.product_ordered_qty, uom.name, COALESCE(pr_line.mrr_qty, 0) AS mrr_qty,
                        pr_line.product_ordered_qty - COALESCE(pr_line.mrr_qty, 0) AS remain_qty, pr_line.last_price_unit,
                        (SELECT SUM(po_line.product_qty) FROM po_pr_line_rel map_table
                            LEFT JOIN purchase_order_line po_line ON po_line.id = map_table.po_line_id
                            LEFT JOIN purchase_order po ON po.id = po_line.order_id WHERE map_table.pr_line_id = pr_line.id) AS po_qty,
                        (SELECT array_to_string( array_agg( po.name ), ',' ) FROM po_pr_line_rel map_table
                            LEFT JOIN purchase_order_line po_line ON po_line.id = map_table.po_line_id
                            LEFT JOIN purchase_order po ON po.id = po_line.order_id WHERE map_table.pr_line_id = pr_line.id) AS po_no
                FROM 
                      purchase_requisition_line pr_line
                      LEFT JOIN purchase_requisition pr ON pr.id = pr_line.requisition_id
                      LEFT JOIN product_uom uom ON uom.id = pr_line.product_uom_id
                      LEFT JOIN product_product pp ON pr_line.product_id = pp.id
                      LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE pr.state = 'done' AND pr.purchase_from = 'ho' AND 
                pr_line.product_ordered_qty - COALESCE(pr_line.mrr_qty, 0) > 0
"""

    @api.multi
    def render_html(self,docids,data=None):

        report_title = ''

        record_list = []

        if data['report_type'] == 'local':

            self.sql_str += " AND pr.purchase_by IN ('cash','credit')"
            report_title = 'Pending Local Purchase Report'

        else:
            self.sql_str += " AND pr.purchase_by IN ('lc','tt')"
            report_title = 'Pending Foreign Purchase Report'

        self._cr.execute(self.sql_str)
        data_list = self._cr.fetchall()

        for row in data_list:
            list_obj = {}
            list_obj['pr_no'] = row[2]
            list_obj['items'] = row[3]
            list_obj['qty'] = row[4]
            list_obj['unit'] = row[5]
            list_obj['mrr_qty'] = row[6]
            list_obj['remaining_qty'] = row[7]
            list_obj['last_rate'] = formatLang(self.env,row[8])
            list_obj['po_qty'] = row[9]
            list_obj['po_no'] = row[10]
            record_list.append(list_obj)

        docargs = {
            'data': data,
            'report_title':report_title,
            'lists': record_list,

        }
        return self.env['report'].render('purchase_reports.report_pending_purchase', docargs)