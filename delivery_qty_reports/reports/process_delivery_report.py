from odoo import api, fields, models
import time

from datetime import date,datetime



class ProcessDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        do_list = []

        issued_do_sum_list = []
        delivery_qty_sum_list = []
        undelivery_qty_sum_list = []

        stock_picking_pool = self.env['stock.picking'].search([('min_date', '<', data['report_of_day'])])

        for stocks in stock_picking_pool:

            DO_date = datetime.strptime(stocks.min_date, "%Y-%m-%d %H:%M:%S").date()
            DO_Qty = stocks.pack_operation_product_ids.product_qty

            data = {}
            data['partner_id'] = stocks.partner_id.name
            data['do_date'] = DO_date
            data['do_no'] = stocks.name
            data['do_qty'] = DO_Qty
            data['un_delivered_qty'] = stocks.pack_operation_product_ids.product_qty - stocks.pack_operation_product_ids.qty_done
            data['delivered_qty'] = stocks.pack_operation_product_ids.qty_done
            data['product'] = stocks.pack_operation_product_ids.product_id.name

            ## Cross match with DO Date and today's date to get Issued D.O property
            if DO_date == date.today():
                data['issued_do_today'] = DO_Qty
                issued_do_sum_list.append(data['issued_do_today'])
            else:
                data['issued_do_today'] = ''

            sale_order_pool = self.env['sale.order'].search([('name', '=', stocks.origin)])
            if sale_order_pool:
                for s in sale_order_pool:
                    data['uom'] = s.order_line.product_uom.name
            else:
                data['uom'] = ''

            delivery_qty_sum_list.append(data['delivered_qty'])
            undelivery_qty_sum_list.append(data['un_delivered_qty'])
            do_list.append(data)


        docargs = \
            {
                'do_list': do_list,
                'issued_do_sum_list': sum(issued_do_sum_list),
                'delivery_qty_sum_list': sum(delivery_qty_sum_list),
                'undelivery_qty_sum_list': sum(undelivery_qty_sum_list),
            }

        return self.env['report'].render('delivery_qty_reports.report_daily_delivery_products', docargs)