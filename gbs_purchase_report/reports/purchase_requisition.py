from odoo import models, fields, api, _
from odoo.tools.misc import formatLang


class PurchaseRequisitionReport(models.AbstractModel):
    _name = 'report.gbs_purchase_report.report_purchase_requisition'

    sql_str = """SELECT
                    pr.id AS requisition_id,
                    pr.name AS requisition_name,
                    prl.product_id AS product_id,
                    pr.requisition_date AS requisition_date,
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
                                pr.id AS requisition_id,
                                array_agg(sp.mrr_no) AS mrr_no
                            FROM
                                stock_picking AS sp
                                JOIN purchase_order AS po ON po.name = sp.origin AND po.purchase_by IN ('cash', 'credit', 'tt')
                                JOIN purchase_requisition AS pr ON pr.id = po.requisition_id
                            WHERE
                                sp.check_mrr_button = true
                            GROUP BY
                                pr.id)
                            UNION ALL
                            (SELECT
                                pr.id AS requisition_id,
                                array_agg(sp.mrr_no) AS mrr_no
                            FROM
                                po_lc_rel AS plr
                                JOIN purchase_order AS po ON po.id = plr.po_id AND po.purchase_by = 'lc'
                                JOIN purchase_requisition AS pr ON pr.id = po.requisition_id
                                JOIN letter_credit AS lc ON lc.id = plr.lc_id
                                JOIN stock_picking AS sp ON sp.origin = lc.name AND sp.check_mrr_button = true
                            GROUP BY
                                pr.id)) AS tbl_temp ON tbl_temp.requisition_id = pr.id
                WHERE
                    DATE(pr.requisition_date) BETWEEN %s AND %s
    """

    @api.multi
    def render_html(self, docids, data=None):
        report_data = self.get_data(data)
        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('gbs_purchase_report.report_purchase_requisition', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.multi
    def get_data(self, data):
        # REPORT DATA (dictionary)
        report_data = {}

        if data['pr_no']:
            self.sql_str += " AND pr.name = '%s'" % (data['pr_no'])
        if data['type'] != 'all':
            self.sql_str += " AND pr.region_type = '%s'" % (data['type'])
        if data['operating_unit_ids']:
            self.sql_str += " AND pr.operating_unit_id IN %s" % (data['operating_unit_ids'])
        if data['is_only_pending']:
            self.sql_str += " AND (prl.product_ordered_qty - COALESCE(prl.mrr_qty, 0)) <> 0"

        # ORDER BY
        self.sql_str += " ORDER BY pr.id, prl.product_id, pr.requisition_date"

        # QUERY EXECUTION
        self._cr.execute(self.sql_str, (data['date_from'], data['date_to']))

        # FETCH DATA, MAKE REPORT DATA OBJECT
        for val in self._cr.fetchall():
            if val[0] not in report_data:
                report_data[val[0]] = {}
                report_data[val[0]]['requisition_name'] = val[1]
                report_data[val[0]]['products'] = []

                report_data[val[0]]['products'].append({'date': val[3],
                                                        'mrr_no': val[4],
                                                        'internal_ref': val[5],
                                                        'product_name': val[6],
                                                        'narration': val[7],
                                                        'unit': val[8],
                                                        'pr_qty': float(val[9]),
                                                        'mrr_qty': float(val[10]),
                                                        'due_qty': float(val[11])})

            else:
                report_data[val[0]]['products'].append({'date': val[3],
                                                        'mrr_no': val[4],
                                                        'internal_ref': val[5],
                                                        'product_name': val[6],
                                                        'narration': val[7],
                                                        'unit': val[8],
                                                        'pr_qty': float(val[9]),
                                                        'mrr_qty': float(val[10]),
                                                        'due_qty': float(val[11])})

        return report_data
