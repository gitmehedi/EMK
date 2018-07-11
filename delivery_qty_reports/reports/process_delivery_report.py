from odoo import api, fields, models
import time

from datetime import date, datetime


class ProcessDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        do_list = []

        issued_do_sum_list = []
        delivery_qty_sum_list = []
        undelivery_qty_sum_list = []
        total_do_qty = []

        product_id = data['product_id']
        op_unit = data['operating_unit_id']
        report_of_day = data['report_of_day']

        stock_picking_pool = self.env['stock.picking'].search([('move_lines.product_id', '=', product_id),
                                                               ('move_lines.operating_unit_id', '=', op_unit),
                                                               ('min_date', '<=', report_of_day)])

        report_of_day = datetime.strptime(report_of_day, "%Y-%m-%d %H:%M:%S").date()

        for stocks in stock_picking_pool:
            for stock_op in stocks.pack_operation_product_ids:

                DO_date = datetime.strptime(stocks.min_date, "%Y-%m-%d %H:%M:%S").date()
                DO_Qty = stock_op.product_qty

                data = {}
                data['partner_id'] = stocks.partner_id.name
                data['do_date'] = DO_date
                data['do_no'] = stocks.delivery_order_id.name
                data['do_qty'] = DO_Qty
                data['un_delivered_qty'] = stock_op.product_qty - stock_op.qty_done
                data['delivered_qty'] = stock_op.qty_done
                data['product'] = stock_op.product_id.name + " ("+stock_op.product_id.attribute_value_ids.name+")"

                ## Cross match with DO Date and today's date to get Issued D.O property
                if DO_date == date.today():
                    data['issued_do_today'] = DO_Qty
                    issued_do_sum_list.append(data['issued_do_today'])
                else:
                    data['issued_do_today'] = ''

            sale_order_pool = self.env['sale.order'].search([('name', '=', stocks.origin)])
            if sale_order_pool:
                for s in sale_order_pool.order_line:
                    data['uom'] = s.product_uom.name
            else:
                data['uom'] = '-'

            delivery_qty_sum_list.append(data['delivered_qty'])
            undelivery_qty_sum_list.append(data['un_delivered_qty'])
            total_do_qty.append(data['do_qty'])

            do_list.append(data)


        product_pool = self.env['product.product'].search([('id','=',product_id)])
        product_name_for_report = product_pool.name  + " ("+product_pool.attribute_value_ids.name+")"

        op_unit_pool = self.env['operating.unit'].search([('id','=',op_unit)])

        docargs = \
            {
                'do_list': do_list,
                'report_of_day': report_of_day,
                'issued_do_sum_list': sum(issued_do_sum_list),
                'delivery_qty_sum_list': sum(delivery_qty_sum_list),
                'undelivery_qty_sum_list': sum(undelivery_qty_sum_list),
                'total_do_qty': sum(total_do_qty),
                'product_name_for_report': product_name_for_report,
                'operating_unit_name':op_unit_pool.name
            }

        return self.env['report'].render('delivery_qty_reports.report_daily_delivery_products', docargs)