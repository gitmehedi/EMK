from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class PurchaseRequisitionInfoXLSX(ReportXlsx):

    @staticmethod
    def get_operating_unit_name(obj):
        name = ''
        for rec in obj.operating_unit_ids:
            name += rec.name + ', '
        return name[:-2]

    def get_data(self, obj):
        # main sql for testing
        full_sql = """SELECT
                            pr.id AS pr_id,
                            pr.name AS pr_name,
                            (PRL_TBL.pr_confirm_date+interval '6h') AS pr_confirm_date,
                            (PRL_TBL.pr_validate_date+interval '6h') AS pr_validate_date,
                            (PRL_TBL.pr_approve_date+interval '6h') AS pr_approve_date,
                            (PRL_TBL.pr_done_date+interval '6h')AS pr_done_date,
                            PRPO_TBL.po_id,
                            PRPO_TBL.po_name,
                            (POAL.perform_date+interval '6h') AS po_approve_date,
                            MRR_TBL.mrr_no,
                            MRR_TBL.challan_no,
                            (MRR_TBL.challan_date+interval '6h') AS challan_date,
                            (MRR_TBL.qc_approve_date+interval '6h') AS qc_approve_date,
                            (MRR_TBL.ss_validate_date+interval '6h') AS ss_validate_date,
                            (MRR_TBL.ss_ac_approve_date+interval '6h') AS ss_ac_approve_date,
                            (MRR_TBL.ss_approve_date+interval '6h') AS ss_approve_date
                        FROM
                            purchase_requisition pr
                            LEFT JOIN ((SELECT
                                            pr.id AS pr_id,
                                            pr.name AS pr_name,
                                            po.id AS po_id,
                                            po.name AS po_name
                                        FROM
                                            purchase_requisition pr
                                            INNER JOIN purchase_order po ON po.requisition_id=pr.id)
                                        UNION
                                        (SELECT
                                            pr.id AS pr_id,
                                            pr.name AS pr_name,
                                            po.id AS po_id,
                                            po.name AS po_name
                                        FROM
                                            purchase_requisition pr
                                            INNER JOIN purchase_requisition_purchase_rfq_rel prprl ON prprl.purchase_requisition_id=pr.id
                                            INNER JOIN purchase_rfq rfq ON rfq.id=prprl.purchase_rfq_id
                                            INNER JOIN purchase_order po ON po.rfq_id=rfq.id)) PRPO_TBL ON PRPO_TBL.pr_id=pr.id
                            LEFT JOIN (SELECT 
                                            SS_TBL.po_id,
                                            SS_TBL.po_name,
                                            SS_TBL.mrr_no,
                                            SS_TBL.challan_no,
                                            SS_TBL.challan_date,
                                            QCL_TBL.perform_date AS qc_approve_date,
                                            SSL_TBL.ss_validate_date,
                                            SSL_TBL.ss_ac_approve_date,
                                            SSL_TBL.ss_approve_date
                                        FROM
                                            ((SELECT
                                                po.id AS po_id,
                                                po.name AS po_name,
                                                ss.id AS ss_picking_id,
                                                ss.mrr_no,
                                                (SELECT challan_bill_no FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                                    WHERE rg.origin=po.name AND spt.code='incoming' LIMIT 1) AS challan_no,
                                                (SELECT challan_date FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                                    WHERE rg.origin=po.name AND spt.code='incoming' LIMIT 1) AS challan_date,
                                                (SELECT qc.id FROM stock_picking qc JOIN stock_location sl ON sl.id=qc.location_dest_id 
                                                    WHERE qc.origin=po.name AND sl.name='Quality Control' LIMIT 1) AS qc_picking_id
                                            FROM
                                                purchase_order po
                                                LEFT JOIN stock_picking ss ON ss.origin=po.name AND (ss.check_ac_approve_button=true OR ss.check_approve_button=true OR ss.check_mrr_button=true)
                                            WHERE
                                                po.purchase_by IN ('cash', 'credit', 'tt'))
                                            UNION
                                            (SELECT
                                                po.id AS po_id,
                                                po.name AS po_name,
                                                ss.id AS ss_picking_id,
                                                ss.mrr_no,
                                                (SELECT challan_bill_no FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                                    WHERE rg.origin=lc.name AND spt.code='incoming' LIMIT 1) AS challan_no,
                                                (SELECT challan_date FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                                    WHERE rg.origin=po.name AND spt.code='incoming' LIMIT 1) AS challan_date,
                                                (SELECT qc.id FROM stock_picking qc JOIN stock_location sl ON sl.id=qc.location_dest_id 
                                                    WHERE qc.origin=lc.name AND sl.name='Quality Control' LIMIT 1) AS qc_picking_id
                                            FROM
                                                purchase_order po
                                                LEFT JOIN po_lc_rel plr ON plr.po_id=po.id
                                                LEFT JOIN letter_credit lc ON lc.id=plr.lc_id
                                                LEFT JOIN stock_picking ss ON ss.origin=lc.name AND (ss.check_ac_approve_button=true OR ss.check_approve_button=true OR ss.check_mrr_button=true)
                                            WHERE
                                                po.purchase_by='lc')) AS SS_TBL
                                            LEFT JOIN stock_picking_action_log QCL_TBL ON QCL_TBL.picking_id=SS_TBL.qc_picking_id
                                            LEFT JOIN (SELECT
                                                            picking_id AS ss_picking_id,
                                                            MAX(validate_date) AS ss_validate_date,
                                                            MAX(ac_approve_date) AS ss_ac_approve_date,
                                                            MAX(approve_date) AS ss_approve_date
                                                        FROM
                                                        (SELECT    
                                                            picking_id,
                                                            CASE ua.code
                                                              WHEN 6 THEN perform_date
                                                              ELSE NULL
                                                            END AS validate_date,
                                                            CASE ua.code
                                                              WHEN 8 THEN perform_date
                                                              ELSE NULL
                                                            END AS ac_approve_date,
                                                            CASE ua.code
                                                              WHEN 7 THEN perform_date
                                                              ELSE NULL
                                                            END AS approve_date
                                                        FROM      
                                                            stock_picking_action_log spal
                                                            JOIN users_action ua ON ua.id=spal.action_id) AS TBL_01
                                                        GROUP BY
                                                            picking_id) AS SSL_TBL ON SSL_TBL.ss_picking_id=SS_TBL.ss_picking_id) MRR_TBL ON MRR_TBL.po_id=PRPO_TBL.po_id
                            LEFT JOIN purchase_order_action_log POAL ON POAL.order_id=PRPO_TBL.po_id
                            LEFT JOIN (SELECT
                                            requisition_id AS pr_id,
                                            MAX(pr_confirm_date) AS pr_confirm_date,
                                            MAX(pr_validate_date) AS pr_validate_date,
                                            MAX(pr_approve_date) AS pr_approve_date,
                                            MAX(pr_done_date) AS pr_done_date
                                        FROM
                                        (SELECT    
                                            requisition_id,
                                            CASE ua.code
                                              WHEN 1 THEN perform_date
                                              ELSE NULL
                                            END AS pr_confirm_date,
                                            CASE ua.code
                                              WHEN 2 THEN perform_date
                                              ELSE NULL
                                            END AS pr_validate_date,
                                            CASE ua.code
                                              WHEN 3 THEN perform_date
                                              ELSE NULL
                                            END AS pr_approve_date,
                                            CASE ua.code
                                              WHEN 4 THEN perform_date
                                              ELSE NULL
                                            END AS pr_done_date
                                        FROM      
                                            purchase_requisition_action_log pral
                                            LEFT JOIN users_action ua ON ua.id=pral.action_id) AS TBL
                                        GROUP BY
                                            requisition_id) PRL_TBL ON PRL_TBL.pr_id=pr.id
                """

        # segregated sql
        _stock_select = """SELECT 
                                SS_TBL.po_id,
                                SS_TBL.po_name,
                                SS_TBL.mrr_no,
                                SS_TBL.challan_no,
                                SS_TBL.challan_date,
                                QCL_TBL.perform_date AS qc_approve_date,
                                SSL_TBL.ss_validate_date,
                                SSL_TBL.ss_ac_approve_date,
                                SSL_TBL.ss_approve_date
        """
        _stock_from = """FROM
                            ((SELECT
                                po.id AS po_id,
                                po.name AS po_name,
                                ss.id AS ss_picking_id,
                                ss.mrr_no,
                                (SELECT challan_bill_no FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                    WHERE rg.origin=po.name AND spt.code='incoming' LIMIT 1) AS challan_no,
                                (SELECT challan_date FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                    WHERE rg.origin=po.name AND spt.code='incoming' LIMIT 1) AS challan_date,
                                (SELECT qc.id FROM stock_picking qc JOIN stock_location sl ON sl.id=qc.location_dest_id 
                                    WHERE qc.origin=po.name AND sl.name='Quality Control' LIMIT 1) AS qc_picking_id
                            FROM
                                purchase_order po
                                LEFT JOIN stock_picking ss ON ss.origin=po.name AND (ss.check_ac_approve_button=true OR ss.check_approve_button=true OR ss.check_mrr_button=true)
                            WHERE
                                po.purchase_by IN ('cash', 'credit', 'tt'))
                            UNION
                            (SELECT
                                po.id AS po_id,
                                po.name AS po_name,
                                ss.id AS ss_picking_id,
                                ss.mrr_no,
                                (SELECT challan_bill_no FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                    WHERE rg.origin=lc.name AND spt.code='incoming' LIMIT 1) AS challan_no,
                                (SELECT challan_date FROM stock_picking rg JOIN stock_picking_type spt ON spt.id=rg.picking_type_id 
                                    WHERE rg.origin=lc.name AND spt.code='incoming' LIMIT 1) AS challan_date,
                                (SELECT qc.id FROM stock_picking qc JOIN stock_location sl ON sl.id=qc.location_dest_id 
                                    WHERE qc.origin=lc.name AND sl.name='Quality Control' LIMIT 1) AS qc_picking_id
                            FROM
                                purchase_order po
                                LEFT JOIN po_lc_rel plr ON plr.po_id=po.id
                                LEFT JOIN letter_credit lc ON lc.id=plr.lc_id
                                LEFT JOIN stock_picking ss ON ss.origin=lc.name AND (ss.check_ac_approve_button=true OR ss.check_approve_button=true OR ss.check_mrr_button=true)
                            WHERE
                                po.purchase_by='lc')) AS SS_TBL
        """
        _stock_join = """
                        LEFT JOIN stock_picking_action_log QCL_TBL ON QCL_TBL.picking_id=SS_TBL.qc_picking_id
                        LEFT JOIN (SELECT
                                        picking_id AS ss_picking_id,
                                        MAX(validate_date) AS ss_validate_date,
                                        MAX(ac_approve_date) AS ss_ac_approve_date,
                                        MAX(approve_date) AS ss_approve_date
                                    FROM
                                    (SELECT    
                                        picking_id,
                                        CASE ua.code
                                          WHEN 6 THEN perform_date
                                          ELSE NULL
                                        END AS validate_date,
                                        CASE ua.code
                                          WHEN 8 THEN perform_date
                                          ELSE NULL
                                        END AS ac_approve_date,
                                        CASE ua.code
                                          WHEN 7 THEN perform_date
                                          ELSE NULL
                                        END AS approve_date
                                    FROM      
                                        stock_picking_action_log spal
                                        JOIN users_action ua ON ua.id=spal.action_id) AS TBL_01
                                    GROUP BY
                                        picking_id) AS SSL_TBL ON SSL_TBL.ss_picking_id=SS_TBL.ss_picking_id
        """

        _pr_po_sql = """(SELECT
                                    pr.id AS pr_id,
                                    pr.name AS pr_name,
                                    po.id AS po_id,
                                    po.name AS po_name
                                FROM
                                    purchase_requisition pr
                                    INNER JOIN purchase_order po ON po.requisition_id=pr.id)
                                UNION
                                (SELECT
                                    pr.id AS pr_id,
                                    pr.name AS pr_name,
                                    po.id AS po_id,
                                    po.name AS po_name
                                FROM
                                    purchase_requisition pr
                                    INNER JOIN purchase_requisition_purchase_rfq_rel prprl ON prprl.purchase_requisition_id=pr.id
                                    INNER JOIN purchase_rfq rfq ON rfq.id=prprl.purchase_rfq_id
                                    INNER JOIN purchase_order po ON po.rfq_id=rfq.id)
        """
        _pr_log_sql = """SELECT
                            requisition_id AS pr_id,
                            MAX(pr_confirm_date) AS pr_confirm_date,
                            MAX(pr_validate_date) AS pr_validate_date,
                            MAX(pr_approve_date) AS pr_approve_date,
                            MAX(pr_done_date) AS pr_done_date
                        FROM
                        (SELECT    
                            requisition_id,
                            CASE ua.code
                              WHEN 1 THEN perform_date
                              ELSE NULL
                            END AS pr_confirm_date,
                            CASE ua.code
                              WHEN 2 THEN perform_date
                              ELSE NULL
                            END AS pr_validate_date,
                            CASE ua.code
                              WHEN 3 THEN perform_date
                              ELSE NULL
                            END AS pr_approve_date,
                            CASE ua.code
                              WHEN 4 THEN perform_date
                              ELSE NULL
                            END AS pr_done_date
                        FROM      
                            purchase_requisition_action_log pral
                            LEFT JOIN users_action ua ON ua.id=pral.action_id) AS TBL
                        GROUP BY
                            requisition_id
        """

        _select = """SELECT
                        pr.id AS pr_id,
                        pr.name AS pr_name,
                        (PRL_TBL.pr_confirm_date+interval '6h') AS pr_confirm_date,
                        (PRL_TBL.pr_validate_date+interval '6h') AS pr_validate_date,
                        (PRL_TBL.pr_approve_date+interval '6h') AS pr_approve_date,
                        (PRL_TBL.pr_done_date+interval '6h')AS pr_done_date,
                        PRPO_TBL.po_id,
                        PRPO_TBL.po_name,
                        (POAL.perform_date+interval '6h') AS po_approve_date,
                        MRR_TBL.mrr_no,
                        MRR_TBL.challan_no,
                        MRR_TBL.challan_date,
                        (MRR_TBL.qc_approve_date+interval '6h') AS qc_approve_date,
                        (MRR_TBL.ss_validate_date+interval '6h') AS ss_validate_date,
                        (MRR_TBL.ss_ac_approve_date+interval '6h') AS ss_ac_approve_date,
                        (MRR_TBL.ss_approve_date+interval '6h') AS ss_approve_date
        """
        _from = """FROM
                        purchase_requisition pr
        """
        _join = """LEFT JOIN (""" + _pr_po_sql + """) PRPO_TBL ON PRPO_TBL.pr_id=pr.id
         """ + """ LEFT JOIN (""" + _stock_select + _stock_from + _stock_join + """) MRR_TBL ON MRR_TBL.po_id=PRPO_TBL.po_id
         """ + """ LEFT JOIN purchase_order_action_log POAL ON POAL.order_id=PRPO_TBL.po_id
                   LEFT JOIN (""" + _pr_log_sql + """) PRL_TBL ON PRL_TBL.pr_id=pr.id"""

        _where = """ WHERE pr.operating_unit_id IN %s"""

        if obj.pr_no:
            _where += " AND pr.name = '%s'" % obj.pr_no
        if obj.date_from and obj.date_to:
            _where += " AND pr.requisition_date BETWEEN '%s' AND '%s'" % (obj.date_from, obj.date_to)
        if obj.type != 'all':
            _where += " AND pr.region_type = '%s'" % obj.type
        if obj.is_only_pending:
            _where += " AND pr.state NOT IN ('close', 'cancel')"

        _order_by = """ ORDER BY pr.requisition_date"""

        data_list = []
        # execute the query
        self.env.cr.execute(_select + _from + _join + _where, (tuple(obj.operating_unit_ids.ids),))

        # fetch data
        for row in self.env.cr.dictfetchall():
            data_list.append(row)

        return data_list

    def generate_xlsx_report(self, workbook, data, obj):

        result_data = self.get_data(obj)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # table header cell format
        th_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('PR Action Log')

        # SET CELL WIDTH
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 23)
        sheet.set_column('K:K', 20)

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 10, self.env.user.company_id.name, name_format)
        sheet.merge_range(2, 0, 2, 10, self.env.user.company_id.street, address_format)
        sheet.merge_range(3, 0, 3, 10, self.env.user.company_id.street2, address_format)
        sheet.merge_range(4, 0, 4, 10, self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range(5, 0, 5, 10, "PR Info Report", name_format)

        row_inc = 0
        if obj.pr_no:
            sheet.merge_range(6, 0, 6, 2, "Req. No: " + obj.pr_no, bold)
            row_inc = 1
        if obj.date_from and obj.date_to:
            sheet.merge_range(6, 8, 6, 10, "Date: " + obj.date_from + " To " + obj.date_to, bold)
            row_inc = 1

        sheet.merge_range(6 + row_inc, 0, 6 + row_inc, 2, "Region Type: " + obj.type.capitalize(), bold)
        sheet.merge_range(6 + row_inc, 8, 6 + row_inc, 10, "Operating Unit: " + self.get_operating_unit_name(obj), bold)

        # TABLE HEADER
        row, col = 7 + row_inc, 0
        sheet.write(row, col, 'PR No', th_cell_center)
        sheet.write(row, col + 1, 'PR Approved Date (PIC)', th_cell_center)
        sheet.write(row, col + 2, 'PR Approved Date (HOP)', th_cell_center)
        sheet.write(row, col + 3, 'PO Number', th_cell_center)
        sheet.write(row, col + 4, 'PO Approved Date', th_cell_center)
        sheet.write(row, col + 5, 'Challan Number', th_cell_center)
        sheet.write(row, col + 6, 'Challan Date', th_cell_center)
        sheet.write(row, col + 7, 'QC Approve Date', th_cell_center)
        sheet.write(row, col + 8, 'SS Update Date', th_cell_center)
        sheet.write(row, col + 9, 'MRR No', th_cell_center)
        sheet.write(row, col + 10, 'MRR Approved Date', th_cell_center)

        # TABLE BODY
        row += 1
        for rec in result_data:
            sheet.write(row, col, rec['pr_name'], td_cell_left)
            sheet.write(row, col + 1, rec['pr_validate_date'], td_cell_center)
            sheet.write(row, col + 2, rec['pr_approve_date'], td_cell_center)
            sheet.write(row, col + 3, rec['po_name'], td_cell_left)
            sheet.write(row, col + 4, rec['po_approve_date'], td_cell_center)
            sheet.write(row, col + 5, rec['challan_no'], td_cell_left)
            sheet.write(row, col + 6, rec['challan_date'], td_cell_center)
            sheet.write(row, col + 7, rec['qc_approve_date'], td_cell_center)
            sheet.write(row, col + 8, rec['ss_validate_date'], td_cell_center)
            sheet.write(row, col + 9, rec['mrr_no'], td_cell_center)
            sheet.write(row, col + 10, rec['ss_approve_date'], td_cell_center)
            row += 1


PurchaseRequisitionInfoXLSX('report.purchase_reports.pr_info_xlsx', 'purchase.requisition.info.wizard', parser=report_sxw.rml_parse)
