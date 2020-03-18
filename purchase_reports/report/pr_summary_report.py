from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from collections import OrderedDict
import datetime


class PurchaseRequisitionSummaryReport(models.AbstractModel):
    _name = 'report.purchase_reports.report_pr_summary'

    sql_str = """SELECT
                    pr.id AS requisition_id,
                    pr.name AS requisition_name,
                    prl.product_id AS product_id,
                    DATE(pr.requisition_date) AS requisition_date,
                    tbl_temp.mrr_no AS mrr_no,
                    pp.default_code AS internal_ref,
                    pt.name AS product_name,
                    prl.remark AS narration,
                    pu.name AS unit,
                    prl.product_ordered_qty AS requisition_qty,
                    COALESCE(prl.mrr_qty, 0) AS mrr_qty, 
                    (prl.product_ordered_qty-COALESCE(prl.mrr_qty, 0)) AS due_qty
                FROM
                    purchase_requisition_line AS prl
                    LEFT JOIN purchase_requisition AS pr ON pr.id = prl.requisition_id
                    LEFT JOIN product_product AS pp ON pp.id = prl.product_id
                    LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN product_uom AS pu ON pu.id = prl.product_uom_id
                    LEFT JOIN ((SELECT 
                                    tbl_map.pr_line_id,
                                    array_agg(sp.mrr_no) AS mrr_no
                                FROM 
                                    po_pr_line_rel tbl_map
                                    LEFT JOIN purchase_order_line po_line ON po_line.id = tbl_map.po_line_id
                                    LEFT JOIN purchase_order po ON po.id = po_line.order_id
                                    LEFT JOIN stock_picking sp ON sp.origin = po.name
                                WHERE 
                                    po.purchase_by IN ('cash', 'credit', 'tt') AND sp.check_mrr_button = true
                                GROUP BY
                                    tbl_map.pr_line_id)
                                UNION ALL
                                (SELECT 
                                    tbl_map.pr_line_id,
                                    array_agg(sp.mrr_no) AS mrr_no
                                FROM 
                                    po_pr_line_rel tbl_map
                                    LEFT JOIN purchase_order_line po_line ON po_line.id = tbl_map.po_line_id
                                    LEFT JOIN purchase_order po ON po.id = po_line.order_id 
                                    LEFT JOIN po_lc_rel tbl_map2 ON tbl_map2.po_id = po.id
                                    LEFT JOIN letter_credit lc ON lc.id = tbl_map2.lc_id
                                    LEFT JOIN stock_picking sp ON sp.origin = lc.name
                                WHERE 
                                    po.purchase_by = 'lc' AND sp.check_mrr_button = true
                                GROUP BY
                                    tbl_map.pr_line_id)) AS tbl_temp ON tbl_temp.pr_line_id = prl.id
                WHERE
                    pr.operating_unit_id IN (%s)
    """

    @api.multi
    def render_html(self, docids, data=None):
        report_data = self.get_data(data)
        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('purchase_reports.report_pr_summary', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.multi
    def get_data(self, data):
        # REPORT DATA (dictionary)
        report_data = OrderedDict()

        if data['pr_no']:
            self.sql_str += " AND pr.name = '%s'" % (data['pr_no'])
        if data['date_from'] and data['date_to']:
            self.sql_str += " AND DATE(pr.requisition_date) BETWEEN '%s' AND '%s'" % (data['date_from'], data['date_to'])
        if data['type'] != 'all':
            self.sql_str += " AND pr.region_type = '%s'" % (data['type'])
        if data['is_only_pending']:
            self.sql_str += " AND (prl.product_ordered_qty - COALESCE(prl.mrr_qty, 0)) <> 0"

        # ORDER BY
        self.sql_str += " ORDER BY DATE(pr.requisition_date), pr.id"

        # QUERY EXECUTION
        # self._cr.execute(self.sql_str, (data['date_from'], data['date_to']))
        self._cr.execute(self.sql_str, (data['operating_unit_ids']))

        # FETCH DATA, MAKE REPORT DATA OBJECT
        for val in self._cr.fetchall():
            if val[0] not in report_data:
                report_data[val[0]] = {}
                report_data[val[0]]['requisition_name'] = val[1]
                report_data[val[0]]['products'] = []

                date_str = datetime.datetime.strptime(val[3], '%Y-%m-%d').strftime('%d-%m-%Y')
                report_data[val[0]]['products'].append({'date': date_str,
                                                        'mrr_no': val[4],
                                                        'internal_ref': val[5],
                                                        'product_name': val[6],
                                                        'narration': val[7],
                                                        'unit': val[8],
                                                        'pr_qty': float(val[9]),
                                                        'mrr_qty': float(val[10]),
                                                        'due_qty': float(val[11])})

            else:
                date_str = datetime.datetime.strptime(val[3], '%Y-%m-%d').strftime('%d-%m-%Y')
                report_data[val[0]]['products'].append({'date': date_str,
                                                        'mrr_no': val[4],
                                                        'internal_ref': val[5],
                                                        'product_name': val[6],
                                                        'narration': val[7],
                                                        'unit': val[8],
                                                        'pr_qty': float(val[9]),
                                                        'mrr_qty': float(val[10]),
                                                        'due_qty': float(val[11])})

        return report_data
