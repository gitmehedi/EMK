from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _
from operator import attrgetter
import datetime


class ItemLedgerReportXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        reportUtility = self.env['report.utility']
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', obj.operating_unit_id.id), ('name', '=', 'Stock')])

        if not location:
            raise UserError(_("There are no stock location for this unit. "
                              "\nPlease create stock location for this unit."))

        date_from = obj.date_from
        date_start = date_from + ' 00:00:00'
        date_to = obj.date_to
        date_end = date_to + ' 23:59:59'
        location_outsource = location.id
        category_id = obj.category_id.id
        product_id = obj.product_id.id
        cat_pool = self.env['product.category']
        product_pool = self.env['product.product']
        cat_lists = []

        report_name = 'Item Ledger Report'
        sheet = workbook.add_worksheet(report_name)
        sheet.set_column(0, 0, 16)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 16)
        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 8})
        name_format_left = workbook.add_format({'align': 'left', 'bold': True, 'size': 8})
        header_format_left = workbook.add_format(
            {'align': 'left', 'border': 1, 'bg_color': '#d7ecfa', 'bold': True, 'size': 8})
        footer_format_left = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': True, 'size': 8})

        footer_format_left_comma_separator = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'border': 1, 'bold': True, 'size': 8})
        normal_format_left = workbook.add_format({'align': 'left', 'size': 8})
        normal_format_left_comma_separator = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'size': 8})
        merged_format_center = workbook.add_format({'align': 'center', 'size': 8})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 7})

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 9, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 9, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 9, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 9, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                          address_format)
        sheet.merge_range(4, 0, 4, 9, "Item Ledger Report", name_format)

        sheet.write(5, 0, "Product Category", name_format_left)
        sheet.merge_range('B6:E6', obj.category_id.name, normal_format_left)
        if obj.product_id:
            product_name = obj.product_id.name_get()[0][1]
        else:
            product_name = ''
        sheet.write(6, 0, "Product Variant", name_format_left)
        sheet.merge_range('B7:E7', product_name, normal_format_left)
        sheet.write(6, 5, "Date", name_format_left)
        sheet.merge_range('G7:J7', reportUtility.get_date_from_string(
            obj.date_from) + ' to ' + reportUtility.get_date_from_string(
            obj.date_to), normal_format_left)
        sheet.write(7, 0, "Operating Unit", name_format_left)
        sheet.merge_range('B8:E8', obj.operating_unit_id.name, normal_format_left)

        ######

        sheet.write(8, 0, "Date", header_format_left)
        sheet.write(8, 1, "Reference", header_format_left)
        sheet.write(8, 2, "UoM", header_format_left)
        sheet.write(8, 3, "In Qty", header_format_left)
        sheet.write(8, 4, "Out Qty", header_format_left)
        sheet.write(8, 5, "Rate", header_format_left)
        sheet.write(8, 6, "Type", header_format_left)
        sheet.write(8, 7, "Amount In", header_format_left)
        sheet.write(8, 8, "Amount Out", header_format_left)
        #

        if category_id:
            categories = cat_pool.get_categories(category_id)
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'total_dk_qty': 0.0,
                    'total_dk_val': 0.0,
                    'total_in_qty': 0.0,
                    'total_in_val': 0.0,
                    'total_out_qty': 0.0,
                    'total_out_val': 0.0,
                    'total_ck_qty': 0.0,
                    'total_ck_val': 0.0,
                }
            } for val in cat_pool.search([('id', 'in', categories)])}
        else:
            cat_lists = cat_pool.search([], order='name ASC')
            category = {val.name: {
                'product': [],
                'sub-total': {
                    'title': 'SUB TOTAL',
                    'total_dk_qty': 0.0,
                    'total_dk_val': 0.0,
                    'total_in_qty': 0.0,
                    'total_in_val': 0.0,
                    'total_out_qty': 0.0,
                    'total_out_val': 0.0,
                    'total_ck_qty': 0.0,
                    'total_ck_val': 0.0,
                }
            } for val in cat_lists}

        if cat_lists:
            categories = cat_lists.ids
        # else:
        #     categories = cat_lists

        if len(categories) == 1:
            category_param = "(" + str(obj.category_id.id) + ")"
        else:
            category_param = str(tuple(categories))

        if product_id:
            product_param = "(" + str(obj.product_id.id) + ")"
        else:
            product_list = product_pool.search([('product_tmpl_id.categ_id.id', 'in', categories)])
            if len(product_list) == 1:
                product_param = "(" + str(product_list.id) + ")"
            elif len(product_list) > 1:
                product_param = str(tuple(product_list.ids))
            else:
                product_param = '(0)'

        sql_in_tk = '''
                                    SELECT product_id, 
                                           NAME, 
                                           origin,
                                           code,
                                            'IN' as type,
                                            move_date,
                                           uom_name, 
                                           category,
                                           cost_val AS rate,
                                           Sum(qty_in_tk) AS qty_in_tk, 
                                           Sum(val_in_tk) AS value_amount 
                                    FROM   (SELECT sm.product_id, 
                                                   sm.origin,
                                                   pt.NAME, 
                                                   DATE(sm.date) AS move_date,
                                                   pp.default_code                          AS code,
                                                   pu.name                                  AS uom_name, 
                                                   pc.name                                  AS category, 
                                                   sm.product_qty                           AS qty_in_tk, 
                                                   sm.product_qty * Coalesce((SELECT ph.cost
                                                     FROM   product_price_history ph
                                                     WHERE  ph.datetime + interval'6h' <= '%s'
                                                            AND pp.id = ph.product_id
                                                     ORDER  BY ph.datetime DESC,ph.id DESC
                                                     LIMIT  1), 0) AS val_in_tk,
                                                   Coalesce((SELECT ph.cost
                                                     FROM   product_price_history ph
                                                     WHERE  ph.datetime + interval'6h' <= '%s'
                                                            AND pp.id = ph.product_id
                                                     ORDER  BY ph.datetime DESC,ph.id DESC
                                                     LIMIT  1), 0)          AS cost_val
                                            FROM   stock_move sm 
                                                   LEFT JOIN stock_picking sp 
                                                          ON sm.picking_id = sp.id 
                                                   LEFT JOIN product_product pp 
                                                          ON sm.product_id = pp.id 
                                                   LEFT JOIN product_template pt 
                                                          ON pp.product_tmpl_id = pt.id 
                                                   LEFT JOIN stock_location sl 
                                                          ON sm.location_id = sl.id 
                                                   LEFT JOIN product_category pc 
                                                          ON pt.categ_id = pc.id
                                                   LEFT JOIN product_uom pu 
                				                          ON( pu.id = pt.uom_id )
                                            WHERE  sm.date + interval'6h' BETWEEN '%s' AND '%s' 
                                                   AND sm.state = 'done' 
                                                   --AND sp.location_type = 'outsource_out' 
                                                   AND sm.location_id <> %s
                                                   AND sm.location_dest_id = %s 
                                                   AND pc.id IN %s
                                                   AND pp.id IN %s
                                           --AND usage like 'internal' 
                                           )t1 
                                    GROUP  BY product_id, 
                                              NAME, 
                                              code,
                                              uom_name,
                                              origin,
                                              move_date,
                                              category,
                                              cost_val 
                                ''' % (
            date_end, date_end, date_start, date_end, location_outsource, location_outsource, category_param,
            product_param)

        sql_out_tk = '''SELECT product_id,
                                   name,
                                   origin,
                                   code,
                                    'OUT' as type,
                                    move_date,
                                   uom_name,
                                   category,
                                   list_price AS rate,
                                   Sum(qty_out_tk)              AS qty_out_tk,
                                   Sum(val_out_tk)              AS value_amount
                            FROM   (SELECT sm.product_id,
                                           sm.origin,
                                           pt.name,
                                           DATE(sm.date) AS move_date,
                                           pp.default_code         AS code,
                                           pu.name                 AS uom_name,
                                           pc.name                 AS category,
                                           sm.product_qty          AS qty_out_tk,
                                           Coalesce((SELECT ph.cost
                                                     FROM   product_price_history ph
                                                     WHERE  ph.datetime + interval'6h' <= '%s'
                                                            AND pp.id = ph.product_id
                                                     ORDER  BY ph.datetime DESC,ph.id DESC
                                                     LIMIT  1), 0) AS list_price,
                                           sm.product_qty * Coalesce((SELECT ph.cost
                                                     FROM   product_price_history ph
                                                     WHERE  ph.datetime + interval'6h' <= '%s'
                                                            AND pp.id = ph.product_id
                                                     ORDER  BY ph.datetime DESC,ph.id DESC
                                                     LIMIT  1), 0) AS val_out_tk
                                    FROM   stock_move sm
                                           LEFT JOIN stock_picking sp
                                                  ON sm.picking_id = sp.id
                                           LEFT JOIN product_product pp
                                                  ON sm.product_id = pp.id
                                           LEFT JOIN product_template pt
                                                  ON pp.product_tmpl_id = pt.id
                                           LEFT JOIN stock_location sl
                                                  ON sm.location_id = sl.id
                                           LEFT JOIN product_category pc
                                                  ON pt.categ_id = pc.id
                                           LEFT JOIN product_uom pu
        				                          ON( pu.id = pt.uom_id )
                                    WHERE  sm.date + interval'6h' BETWEEN '%s' AND '%s'
                                           AND sm.state = 'done'
                                           AND sm.location_id = %s
                                           AND sm.location_dest_id <> %s
                                           AND pc.id IN %s
                                           AND pp.id IN %s
                                   )t1
                            GROUP  BY product_id,
                                      name,
                                      code,
                                      origin,
                                      uom_name,
                                      category,
                                      move_date,
                                      list_price
                                ''' % (
            date_end, date_end, date_start, date_end, location_outsource, location_outsource, category_param,
            product_param)

        item_ledger_vals_list = []

        self.env.cr.execute(sql_in_tk)
        for vals1 in self.env.cr.dictfetchall():
            item_ledger_vals_list.append(vals1)
        self.env.cr.execute(sql_out_tk)
        for vals2 in self.env.cr.dictfetchall():
            item_ledger_vals_list.append(vals2)
        sorted_item_ledger_vals_list = sorted(item_ledger_vals_list, key=lambda d: d['move_date'])

        row_no = 9
        total_in_qty = 0
        total_out_qty = 0
        total_rate = 0
        total_amount_in = 0
        total_amount_out = 0
        for vals in sorted_item_ledger_vals_list:
            sheet.write(row_no, 0, reportUtility.get_date_from_string(vals['move_date']), normal_format_left)
            sheet.write(row_no, 1, vals['origin'], normal_format_left)
            sheet.write(row_no, 2, vals['uom_name'], normal_format_left)
            # in qty
            if vals['type'] == 'IN':
                sheet.write(row_no, 3, vals['qty_in_tk'], normal_format_left_comma_separator)
                total_in_qty = total_in_qty + vals['qty_in_tk']
            else:
                total_in_qty = total_in_qty + 0
                sheet.write(row_no, 3, '0', normal_format_left_comma_separator)
            # out qty
            if vals['type'] == 'OUT':
                sheet.write(row_no, 4, vals['qty_out_tk'], normal_format_left_comma_separator)
                total_out_qty = total_out_qty + vals['qty_out_tk']
            else:
                sheet.write(row_no, 4, '0', normal_format_left_comma_separator)
                total_out_qty = total_out_qty + 0
            # rate
            sheet.write(row_no, 5, vals['rate'], normal_format_left_comma_separator)
            total_rate = total_rate + vals['rate']
            # type
            sheet.write(row_no, 6, vals['type'], normal_format_left)
            # amount in
            if vals['type'] == 'IN':
                sheet.write(row_no, 7, vals['value_amount'], normal_format_left_comma_separator)
                total_amount_in = total_amount_in + vals['value_amount']
            else:
                sheet.write(row_no, 7, '0', normal_format_left_comma_separator)
                total_amount_in = total_amount_in + 0

            # amount out
            if vals['type'] == 'OUT':
                total_amount_out = total_amount_out + vals['value_amount']
                sheet.write(row_no, 8, vals['value_amount'], normal_format_left_comma_separator)
            else:
                total_amount_out = total_amount_out + 0
                sheet.write(row_no, 8, '0', normal_format_left_comma_separator)
            row_no = row_no + 1

        sheet.write(row_no, 0, 'Closing Information', footer_format_left)
        sheet.write(row_no, 1, '', footer_format_left)
        sheet.write(row_no, 2, '', footer_format_left)
        sheet.write(row_no, 3, total_in_qty, footer_format_left_comma_separator)
        sheet.write(row_no, 4, total_out_qty, footer_format_left_comma_separator)
        sheet.write(row_no, 5, total_rate, footer_format_left_comma_separator)
        sheet.write(row_no, 6, '', footer_format_left)
        sheet.write(row_no, 7, total_amount_in, footer_format_left_comma_separator)
        sheet.write(row_no, 8, total_amount_out, footer_format_left_comma_separator)
        data['name'] = 'Item Ledger Report'


ItemLedgerReportXLSX('report.item_ledger_report.item_ledger_report_xlsx',
                     'item.ledger.report.wizard', parser=report_sxw.rml_parse)
